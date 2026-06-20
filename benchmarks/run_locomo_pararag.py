from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI
from dotenv import find_dotenv, load_dotenv
from tqdm import tqdm
import argparse
import asyncio
import json
import time
import os

from benchmarks.utils import parse_locomo_timestamp
from benchmarks.prompts import ANSWER_PROMPT_4_2
from pararag import ParaRAGMemory, MemoryEntry, Profile, JsonLogger, get_console


load_dotenv(find_dotenv())


async def ingest_conversation(conversations: list[dict], memory: ParaRAGMemory, json_logger: JsonLogger) -> None:
    """Extracts memories from conversations and ingests them into vector database"""
    last_msg_id = None

    for msg in tqdm(conversations, desc="Extracting memories", leave=True):
        timestamp = parse_locomo_timestamp(msg["timestamp"])
        speaker = msg["speaker"]
        msg_id = msg["id"]
        last_msg_id = msg_id

        # Include blip caption in the user msg if present
        blip_caption = msg.get("blip_caption")
        if blip_caption:
            user_msg = f"{msg['text']} (image attachment: {blip_caption})"
        else:
            user_msg = msg["text"]

        # Print logs
        get_console().print_locomo_msg(user_msg, speaker, msg_id)

        # Save json logs
        json_logger.log_msg(speaker, user_msg, msg_id)

        # Add message to memory
        await memory.add_user_msg(
            user_msg=user_msg,
            speaker=speaker,
            timestamp=timestamp,
            msg_id=msg_id,
        )

    await memory.force_profile_update(msg_id=last_msg_id)


def memories_to_str(memories: list[MemoryEntry]) -> str:
    return "\n".join([str(memory) for memory in memories])

def profiles_to_str(profiles: list[Profile]) -> str:
    return "\n\n".join([str(profile) for profile in profiles])

def get_locomo_speakers(dataset_path: str, sample_id: str) -> list[str]:
    with open(dataset_path, mode="r", encoding="utf-8") as file:
        data = json.load(file)
    
    conversation = data[sample_id]["conversation"]
    return [conversation[0]["speaker"], conversation[1]["speaker"]]


async def answer_question(qa_item: dict, memory: ParaRAGMemory, llm: ChatOpenAI) -> dict:
    """Retrieves memories and answers a single question from locomo benchmark while measuring latency and maintaining metadata"""
    question = qa_item["question"]

    # Retrieve memories and measure latency
    start = time.perf_counter()
    memories = await memory.retrieve_memories(question)
    profiles = await memory.retrieve_user_profiles()
    retrieval_latency = time.perf_counter() - start

    memories_str = memories_to_str(memories)
    profiles_str = profiles_to_str(profiles)

    prompt = ANSWER_PROMPT_4_2.format(
        question=question,
        profiles=profiles_str,
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
        "profiles": profiles_str,
        "prompt": prompt,
        "response": response.content,
        "search_time": retrieval_latency,
        "response_time": response_latency,
    }


async def main(
    memory_version: str, 
    dataset_path: str, 
    output_path: str, 
    logs_path: str, 
    json_logs_path: str,
    rerun_retrieval: bool,
) -> None:
    llm = ChatOpenAI(model=os.getenv("ANSWER_MODEL"))

    # Read locomo json file
    with open(file=dataset_path, mode="r") as file:
        data = json.load(file)

    # Init json logger
    json_logger = JsonLogger(output_path=json_logs_path)

    result = {}
    for sample_id, sample in tqdm(data.items(), desc="Processing conversations"):
        # Update logger
        json_logger.set_sample_id(sample_id)

        # Init and clear memory
        memory = ParaRAGMemory(
            memory_version=memory_version,
            json_logger=json_logger,
            users=get_locomo_speakers(dataset_path, sample_id),
        )

        # Clear memory and ingest unless only rerunning retrieval
        if not rerun_retrieval:
            await memory.clear_collection()
            await memory.delete_profiles()
            await memory.init_profile_store()

            # Ingest memories
            await ingest_conversation(
                conversations=sample["conversation"], 
                memory=memory, 
                json_logger=json_logger,
            )

        qa_items = sample["question"]
        sample_result = []

        # Generate responses to test questions concurrently in batches
        batch_size = 10
        for i in tqdm(range(0, len(qa_items), batch_size), desc=f"Answering {sample_id}", leave=True):
            qa_batch = qa_items[i: i + batch_size]
            coroutines = [answer_question(qa_item, memory, llm) for qa_item in qa_batch]
            qa_results = await asyncio.gather(*coroutines)
            sample_result.extend(qa_results)

        # Append it to results
        result[sample_id] = sample_result

        # Save json logs
        json_logger.save_sample_logs()
    
    # Write the results
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
        "--memory-version",
        type=str,
        required=True,
    )
    parser.add_argument(
        "--dataset-path",
        type=str,
        default="data/locomo/locomo10_rag_with_metadata.json"
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
        "--rerun-retrieval",
        action="store_true"
    )
    args = parser.parse_args()

    asyncio.run(
        main(
            memory_version=args.memory_version,
            dataset_path=args.dataset_path,
            output_path=args.output_path,
            logs_path=args.logs_path,
            json_logs_path=args.json_logs_path,
            rerun_retrieval=args.rerun_retrieval,
        )
    )
