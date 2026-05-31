from langgraph.runtime import Runtime
from langchain_core.messages import SystemMessage
from pydantic import BaseModel, Field
from dotenv import find_dotenv, load_dotenv
from typing import Literal
import asyncio
import os

from pararag.memory.services.memory_retrieval_service import MemoryRetrievalService
from pararag.orchestration.simple_decomposition.update.nodes import GraphState
from pararag.orchestration.shared.prompts import MEMORY_DEDUPLICATION_PROMPT
from pararag.orchestration.shared.types import MemoryContext
from pararag.orchestration.shared.utils import memories_to_str
from pararag.shared.types import Collection
from pararag.shared.console import get_console
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
    deduplicated_assertions: list[str]


async def decide_memory_insertion(
    memory_content: str, 
    retrieval_service: MemoryRetrievalService,
) -> UpdateDecision:
    """Decide whether the new memory should be inserted into the store. If it is a duplicate or very similar to existing memories it should not."""
    
    # Choose a different collection for locomo benchmark
    collection = Collection.LOCOMO if os.getenv("FOR_LOCOMO") == "true" else Collection.ASSERTIONS

    # Retrieve most similar existing memories
    similar_memories = await retrieval_service.retrieve_dense(
        query=memory_content,
        collection=collection,
    )
    memories_str = memories_to_str(similar_memories)

    # Decide whether the new memory is unlike the past memories
    llm = get_llm().with_structured_output(UpdateDecision)
    prompt = MEMORY_DEDUPLICATION_PROMPT.format(
        new_memory=memory_content,
        past_memories=memories_str,
    )
    return await llm.ainvoke([SystemMessage(prompt)])


async def update_memory(state: DeduplicationState, runtime: Runtime[MemoryContext]) -> dict:
    """Updates memory with all non-duplicate entries concurrently"""
    update_service = runtime.context["update_service"]
    retrieval_service = runtime.context["retrieval_service"]

    # Decide on memory insertions concurrently
    decisions = await asyncio.gather(
        *[
            decide_memory_insertion(memory_content, retrieval_service)
            for memory_content in state["assertions"]
        ]
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

    # Choose a different collection for locomo benchmark
    collection = Collection.LOCOMO if os.getenv("FOR_LOCOMO") == "true" else Collection.ASSERTIONS

    # Insert memories with positive decisons
    memories_to_insert = [item.memory for item in memories_with_decisions if item.decision == "yes"]

    # Print logs
    get_console().print_deduplication([memory.model_dump() for memory in memories_with_decisions])

    # Concurrent insertion
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

    # Update graph state for the process to be visible in tracing
    return {
        "update_decisions": memories_with_decisions,
        "deduplicated_assertions": memories_to_insert,
    }
