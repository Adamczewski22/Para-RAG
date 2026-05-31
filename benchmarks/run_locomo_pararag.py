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
from pararag import ParaRAGMemory, MemoryEntry, get_console


# The same prompt as in the baseline memobase RAG is used for fair evaluation.
# The only change is replacement of word "conversation" by "memory" as the context is supplied in different form.
PROMPT = """
You are a helpful assistant that can answer questions based on the provided context.
If the question involves timing, use the memory date for reference.
Provide the shortest possible answer.
Use words directly from the memory when possible.
Avoid using subjects in your answer.

# Question:
{question}

# Context:
{context}

# Short answer:
"""

load_dotenv(find_dotenv())


async def ingest_conversation(conversations: list[dict], memory: ParaRAGMemory) -> None:
    """Extracts memories from conversations and ingests them into vector database"""
    for msg in tqdm(conversations, desc="Extracting memories", leave=True):
        timestamp = parse_locomo_timestamp(msg["timestamp"])

        get_console().print_locomo_msg(
            content=msg["text"],
            speaker=msg["speaker"]
        )

        # Add message to memory
        await memory.add_user_msg(
            user_msg=msg["text"],
            speaker=msg["speaker"],
            timestamp=timestamp,
        )


def memories_to_str(memories: list[MemoryEntry]) -> str:
    return "\n".join([str(memory) for memory in memories])


async def answer_question(qa_item: dict, memory: ParaRAGMemory, llm: ChatOpenAI) -> dict:
    """Retrieves memories and answers a single question from locomo benchmark while measuring latency and maintaining metadata"""
    question = qa_item["question"]

    # Retrieve memories and measure latency
    start = time.perf_counter()
    memories = await memory.retrieve_memories(question)
    retrieval_latency = time.perf_counter() - start
    memories_str = memories_to_str(memories)

    prompt = PROMPT.format(
        question=question,
        context=memories_str,
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
        "response": response.content,
        "search_time": retrieval_latency,
        "response_time": response_latency,
    }


async def main(dataset_path: str, output_path: str, logs_path: str) -> None:
    llm = ChatOpenAI(model=os.getenv("MODEL"))

    # Read locomo json file
    with open(file=dataset_path, mode="r") as file:
        data = json.load(file)

    result = {}
    for sample_id, sample in tqdm(data.items(), desc="Processing conversations"):
        # Ingest memories
        memory = ParaRAGMemory()
        await memory.clear_collection() # extra reset to be safe
        await ingest_conversation(sample["conversation"], memory)

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

        # Reset the memory since the next sample will be an independent conversation
        await memory.clear_collection()
    
    # Write the results
    with open(file=output_path, mode="w") as file:
        json.dump(result, file, indent=4, ensure_ascii=False)
    
    # Save the logs of debugging and analysis
    get_console().save_html(path=logs_path)


if __name__ == "__main__":
    if not os.getenv("FOR_LOCOMO") == "true":
        raise ValueError("FOR_LOCOMO env var must be set to `true` for evaluation mode")

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--dataset-path",
        type=str,
        default="data/locomo/locomo10_rag.json"
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
    args = parser.parse_args()

    asyncio.run(
        main(
            dataset_path=args.dataset_path,
            output_path=args.output_path,
            logs_path=args.logs_path,
        )
    )
