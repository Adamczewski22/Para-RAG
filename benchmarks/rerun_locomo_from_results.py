from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI
from dotenv import find_dotenv, load_dotenv
from tqdm import tqdm
import argparse
import asyncio
import json
import time
import os

from prompts import ANSWER_PROMPT_3


load_dotenv(find_dotenv())


async def answer_question(qa_item: dict, llm: ChatOpenAI) -> dict:
    """Aswers a single question from locomo benchmark based on given context while measuring latency and maintaining metadata"""
    prompt = ANSWER_PROMPT_3.format(
        question=qa_item["question"],
        context=qa_item["context"],
    )

    start = time.perf_counter()
    response = await llm.ainvoke([SystemMessage(content=prompt)])
    response_time = time.perf_counter() - start

    return {
        "question": qa_item["question"],
        "answer": qa_item["answer"],
        "category": qa_item["category"],
        "context": qa_item["context"],
        "response": response.content,
        "search_time": qa_item["search_time"],
        "response_time": response_time,
    }


async def main(results_path: str, output_path: str):
    llm = ChatOpenAI(model=os.getenv("MODEL"))

    with open(results_path, mode="r", encoding="utf-8") as file:
        data = json.load(file)
    
    result = {}
    for sample_id, sample in tqdm(data.items(), desc="Processing conversations"):
        batch_size = 10
        sample_result = []

        for i in tqdm(range(0, len(sample), batch_size), desc="Answering questions"):
            qa_batch = sample[i: i + batch_size]
            coroutines = [answer_question(qa, llm) for qa in qa_batch]
            results = await asyncio.gather(*coroutines)
            sample_result.extend(results)
        
        result[sample_id] = sample_result
    
    with open(output_path, mode="w", encoding="utf-8") as file:
        json.dump(result, file, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--results-path",
        type=str,
        required=True,
    )

    parser.add_argument(
        "--output-path",
        type=str,
        required=True,
    )

    args = parser.parse_args()
    asyncio.run(
        main(
            results_path=args.results_path,
            output_path=args.output_path,
        )
    )
