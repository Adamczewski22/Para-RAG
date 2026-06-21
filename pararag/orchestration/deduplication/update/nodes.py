from langgraph.runtime import Runtime
from langchain_core.messages import SystemMessage
from pydantic import BaseModel, Field
from dotenv import find_dotenv, load_dotenv
from typing import Literal
import asyncio
import os
import time

from pararag.memory.services import memory_retrieval_service
from pararag.memory.services.memory_retrieval_service import MemoryRetrievalService
from pararag.orchestration.simple_decomposition.update.nodes import GraphState
from pararag.orchestration.shared.prompts import MEMORY_DEDUPLICATION_PROMPT_3
from pararag.orchestration.shared.types import MemoryContext
from pararag.orchestration.shared.utils import memories_to_str
from pararag.shared.types import Collection
from pararag.shared.console import get_console
from pararag.shared.logger import aggregate_token_usage, extract_token_usage
from pararag.ai.llm import get_llm


load_dotenv(find_dotenv())

class MemoryWithDecision(BaseModel):
    memory: str
    decision: str
    reason: str

class UpdateDecision(BaseModel):
    decision: Literal["yes", "no"] = Field(description="Your decision on whether the new memory should be inserted into memory. Must be 'yes' or 'no'.")
    reason: str = Field(description="A brief, preferebly one sentence reason justifying your decision")

class DeduplicationState(GraphState):
    update_decisions: list[MemoryWithDecision]
    deduplicated_assertions: list[str] | None


async def decide_memory_insertion(
    memory_content: str, 
    retrieval_service: MemoryRetrievalService,
) -> tuple[UpdateDecision, dict]:
    """Decide whether the new memory should be inserted into the store. If it is a duplicate or very similar to existing memories it should not."""
    
    # Choose a different collection for locomo benchmark
    collection = Collection.LOCOMO if os.getenv("FOR_LOCOMO") == "true" else Collection.ASSERTIONS

    # Retrieve most similar existing memories
    similar_memories = await retrieval_service.retrieve_dense(
        query=memory_content,
        collection=collection,
        embedding_category="deduplication",
    )
    memories_str = memories_to_str(similar_memories)

    # Decide whether the new memory is unlike the past memories
    llm = get_llm().with_structured_output(UpdateDecision, include_raw=True)
    prompt = MEMORY_DEDUPLICATION_PROMPT_3.format(
        new_memory=memory_content,
        past_memories=memories_str,
    )
    response = await llm.ainvoke([SystemMessage(prompt)])

    # Obtain token usage
    token_usage = extract_token_usage(response.get("raw"))
    if response.get("parsing_error") is not None:
        raise response["parsing_error"]
    
    # Return update decision and token usage
    return response["parsed"], token_usage


async def update_memory(state: DeduplicationState, runtime: Runtime[MemoryContext]) -> dict:
    """Updates memory with all non-duplicate entries concurrently"""
    update_service = runtime.context["update_service"]
    retrieval_service = runtime.context["retrieval_service"]

    # Choose a different collection for locomo benchmark
    collection = Collection.LOCOMO if os.getenv("FOR_LOCOMO") == "true" else Collection.ASSERTIONS

    # Skip deduplication if deduplicated assertions are already provided and ingest
    if state["deduplicated_assertions"] is not None:
        # Concurrent insertion
        await asyncio.gather(
            *[
                update_service.update_memory_from_content(
                    content=memory,
                    collection=collection,
                    timestamp=state["timestamp"],
                )
                for memory in state["deduplicated_assertions"]
            ]
        )
        return {}

    # Decide on memory insertions
    deduplication_start = time.perf_counter()
    # Parallel mode
    if state["parallel_mode"]:
        decision_results = await asyncio.gather(
            *[
                decide_memory_insertion(memory_content, retrieval_service)
                for memory_content in state["assertions"]
            ]
    )
    # Sequential mode
    else:
        decision_results = [
            await decide_memory_insertion(memory_content, retrieval_service)
            for memory_content in state["assertions"]
        ]

    decisions = [decision for decision, _ in decision_results]

    # Aggregate token usage for all dedupication decisions
    deduplication_tokens = aggregate_token_usage(
        [token_usage for _, token_usage in decision_results]
    )

    # Merge decisions with their corresponding 
    memories_with_decisions = [
        MemoryWithDecision(
            memory=memory,
            decision=decision.decision,
            reason=decision.reason,
        )
        for memory, decision in zip(state["assertions"], decisions)
    ]

    # Insert memories with positive decisons
    memories_to_insert = [item.memory for item in memories_with_decisions if item.decision == "yes"]
    deduplication_latency = time.perf_counter() - deduplication_start

    # Logs
    memories_with_decisions_dump = [memory.model_dump() for memory in memories_with_decisions]

    get_console().print_deduplication(memories_with_decisions_dump)
    json_logger = runtime.context["json_logger"]
    
    if state["msg_id"] is not None and json_logger is not None:
        json_logger.log_deduplication_latency(
            msg_id=state["msg_id"],
            latency=deduplication_latency,
        )
        if deduplication_tokens:
            json_logger.log_deduplication_tokens(
                msg_id=state["msg_id"],
                token_usage=deduplication_tokens,
            )
        json_logger.log_deduplication(
            msg_id=state["msg_id"],
            memories_with_decisions=memories_with_decisions_dump,
        )

    # Insertion
    if state["parallel_mode"]:
        # Parallel mode
        await asyncio.gather(
            *[
                update_service.update_memory_from_content(
                    content=memory,
                    collection=collection,
                    timestamp=state["timestamp"],
                )
                for memory in memories_to_insert
            ]
        )
    else:
        # Sequential mode
        for memory in memories_to_insert:
            await update_service.update_memory_from_content(
                content=memory,
                collection=collection,
                timestamp=state["timestamp"],
            )

    # Update graph state for the process to be visible in tracing
    return {
        "update_decisions": memories_with_decisions,
        "deduplicated_assertions": memories_to_insert,
    }
