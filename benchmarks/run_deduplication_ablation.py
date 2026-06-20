from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI
from pathlib import Path
from datetime import datetime
from dotenv import find_dotenv, load_dotenv
from tqdm import tqdm
import argparse
import asyncio
import json
import uuid
import time
import os

from benchmarks.utils import parse_locomo_timestamp
from benchmarks.prompts import ANSWER_PROMPT_4_2
from pararag import ParaRAGMemory, MemoryEntry, Profile, JsonLogger, MemoryVersion, Collection, get_console
from pararag.memory.services.memory_update_service import MemoryUpdateService


load_dotenv(find_dotenv())


async def reingest_assertions(memory_update_service: MemoryUpdateService, memories: list[MemoryEntry]) -> None:
    """Reingest assertions from a previous run"""
    batch_size = 10
    for i in range(0, len(memories), batch_size):
        batch = memories[i: i + batch_size]
        await asyncio.gather(
            *[
                memory_update_service.update_memory(
                    memory_entry=memory,
                    collection=Collection.LOCOMO,
                )
                for memory in batch
            ]
        )


def memories_to_str(memories: list[MemoryEntry]) -> str:
    return "\n".join([str(memory) for memory in memories])

def profiles_to_str(profiles: list[Profile]) -> str:
    return "\n\n".join([str(profile) for profile in profiles])

def get_profiles_by_sample_id(previous_results_path: str) -> dict[str, str]:
    profiles_by_id = {}
    
    with open(previous_results_path, mode="r", encoding="utf-8") as file:
        data = json.load(file)
    
    for sample_id, sample_results in data.items():
        profiles = sample_results[0]["profiles"]
        profiles_by_id[sample_id] = profiles
    
    return profiles_by_id

def get_timestamps_by_msg(conversation: list[dict]) -> dict[str, datetime]:
    result = {}
    for msg in conversation:
        result[msg["id"]] = parse_locomo_timestamp(msg["timestamp"])
    return result


def validate_paths(
    dataset_path: str,
    output_path: str,
    logs_path: str,
    json_logs_path: str,
    previous_logs_path: str,
    previous_results_path: str,
) -> None:
    required_existing = [dataset_path, previous_logs_path, previous_results_path]
    missing = [path for path in required_existing if not Path(path).exists()]
    if missing:
        raise FileNotFoundError(f"Required input path(s) do not exist: {missing}")

    required_absent = [output_path, logs_path, json_logs_path]
    existing = [path for path in required_absent if Path(path).exists()]
    if existing:
        raise FileExistsError(f"Output path(s) already exist: {existing}")


async def answer_question(qa_item: dict, memory: ParaRAGMemory, llm: ChatOpenAI, profiles: str) -> dict:
    """Retrieves memories and answers a single question from locomo benchmark while measuring latency and maintaining metadata"""
    question = qa_item["question"]

    # Retrieve memories and measure latency
    start = time.perf_counter()
    memories = await memory.retrieve_memories(question)
    retrieval_latency = time.perf_counter() - start

    memories_str = memories_to_str(memories)

    prompt = ANSWER_PROMPT_4_2.format(
        question=question,
        profiles=profiles,
        memories=memories_str,
    )
    # Generate answer and measure latency
    start = time.perf_counter()
    response = await llm.ainvoke([SystemMessage(content=prompt)])
    response_latency = time.perf_counter() - start

    return {
        "question": question,
        "answer": qa_item["answer"],
        "category": qa_item["category"],
        "context": memories_str,
        "profiles": profiles,
        "prompt": prompt,
        "response": response.content,
        "search_time": retrieval_latency,
        "response_time": response_latency,
    }


async def main(
    dataset_path: str, 
    output_path: str, 
    logs_path: str, 
    json_logs_path: str,
    previous_logs_path: str,
    previous_results_path: str,
) -> None:
    validate_paths(
        dataset_path=dataset_path,
        output_path=output_path,
        logs_path=logs_path,
        json_logs_path=json_logs_path,
        previous_logs_path=previous_logs_path,
        previous_results_path=previous_results_path,
    )

    llm = ChatOpenAI(model=os.getenv("ANSWER_MODEL"))

    # Init json logger
    json_logger = JsonLogger(output_path=json_logs_path)

    # Get past profiles by sample
    profiles_by_sample = get_profiles_by_sample_id(previous_results_path)

    # Read dataset
    with open(dataset_path, mode="r", encoding="utf-8") as file:
        data = json.load(file)

    # Read logs
    with open(previous_logs_path, mode="r", encoding="utf-8") as file:
        logs = json.load(file)

    result = {}
    for sample_id, sample in tqdm(data.items(), desc="Processing conversations"):
        conversation = sample["conversation"]

        # Update logger
        json_logger.set_sample_id(sample_id)

        # Init and clear memory
        memory = ParaRAGMemory(
            memory_version=MemoryVersion.SIMPLE_DECOMPOSITION,
            json_logger=json_logger,
        )
        await memory.clear_collection()

        # Get timestamps by message
        timestamps_by_msg_id = get_timestamps_by_msg(conversation)

        # Reconstruct memories
        memories = []
        ingestion_logs = logs[sample_id]["ingestion"]

        for msg_id, msg_log in ingestion_logs.items():
            for assertion in msg_log["assertions"]:
                memories.append(MemoryEntry(
                    id=str(uuid.uuid4()),
                    content=assertion,
                    date=timestamps_by_msg_id[msg_id],
                ))

        # Ingest previous assertions (memories)
        await reingest_assertions(
            memory_update_service=memory.orchestrator.update_service,
            memories=memories,
        )

        qa_items = sample["question"]
        profiles = profiles_by_sample[sample_id]
        sample_result = []

        # Generate responses to test questions concurrently in batches
        batch_size = 10
        for i in tqdm(range(0, len(qa_items), batch_size), desc=f"Answering {sample_id}", leave=True):
            qa_batch = qa_items[i: i + batch_size]
            coroutines = [answer_question(qa_item, memory, llm, profiles) for qa_item in qa_batch]
            qa_results = await asyncio.gather(*coroutines)
            sample_result.extend(qa_results)

        # Append it to results
        result[sample_id] = sample_result

        # Save json logs
        json_logger.save_sample_logs()

        # Save the results
        with open(file=output_path, mode="w") as file:
            json.dump(result, file, indent=4, ensure_ascii=False)
    
    # Save the logs of debugging and analysis
    get_console().save_html(path=logs_path)
    json_logger.write_logs()


if __name__ == "__main__":
    if not os.getenv("FOR_LOCOMO") == "true":
        raise ValueError("FOR_LOCOMO env var must be set to `true` for evaluation mode")

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--dataset-path",
        type=str,
        required=True,
    )
    parser.add_argument(
        "--output-path",
        type=str,
        required=True,
    )
    parser.add_argument(
        "--logs-path",
        type=str,
        required=True,
    )
    parser.add_argument(
        "--json-logs-path",
        type=str,
        required=True,
    )
    parser.add_argument(
        "--previous-logs-path",
        type=str,
        required=True,
    )
    parser.add_argument(
        "--previous-results-path",
        type=str,
        required=True,
    )
    args = parser.parse_args()

    asyncio.run(
        main(
            dataset_path=args.dataset_path,
            output_path=args.output_path,
            logs_path=args.logs_path,
            json_logs_path=args.json_logs_path,
            previous_logs_path=args.previous_logs_path,
            previous_results_path=args.previous_results_path,
        )
    )
