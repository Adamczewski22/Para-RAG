from langchain_core.messages import SystemMessage
from langgraph.runtime import Runtime
from dotenv import find_dotenv, load_dotenv
from pydantic import BaseModel, Field
from typing import TypedDict
import asyncio
import os
import time

from pararag.orchestration.shared.prompts import QUERY_DECOMPOSITION_PROMPT, LOCOMO_QUERY_DECOMPOSITION_PROMPT
from pararag.orchestration.shared.types import RetrievalContext
from pararag.orchestration.shared.tools import retrieve
from pararag.shared.models import MemoryEntry, Message
from pararag.shared.types import Collection
from pararag.shared.console import get_console
from pararag.shared.logger import extract_token_usage
from pararag.ai.llm import get_llm

load_dotenv(find_dotenv())


class GraphState(TypedDict):
    conversation_history: list[Message]
    conversation_history_str: str
    last_user_msg: Message
    sub_queries: list[str]
    memories: list[MemoryEntry]
    query_decomposition: bool
    parallel_mode: bool

class SubQueries(BaseModel):
    sub_queries: list[str] = Field(description="A list of simple, atomic sub-queries later used for semantic search.")


async def decompose_query(state: GraphState, runtime: Runtime[RetrievalContext]) -> dict:
    """A node that decomposes the user query into atomic sub-queries to be used for parallel retrieval"""
    # If query decomposition is disabled, use only the question as is
    if not state["query_decomposition"]:
        return {"sub_queries": [state["last_user_msg"].content]}

    llm = get_llm().with_structured_output(SubQueries, include_raw=True)

    # Prompt suited for locomo evaluation: retrieval for a question from the benchmark
    if os.getenv("FOR_LOCOMO") == "true":
        prompt = LOCOMO_QUERY_DECOMPOSITION_PROMPT.format(
            question=state["last_user_msg"].content,
        )

    # Prompt suited for main use case: retrieval during assistant and user conversation.
    else:
        prompt = QUERY_DECOMPOSITION_PROMPT.format(
            conversation_history=state["conversation_history_str"],
            user_query=str(state["last_user_msg"]),
        )

    # Extract sub queries
    decomposition_start = time.perf_counter()
    response = await llm.ainvoke([SystemMessage(prompt)])
    decomposition_latency = time.perf_counter() - decomposition_start

    # Obtain token usage
    retrieval_tokens = extract_token_usage(response.get("raw"))
    if response.get("parsing_error") is not None:
        raise response["parsing_error"]
    
    result = response["parsed"]

    # Emit logs
    get_console().print_queries(
        queries=result.sub_queries,
        query=state["last_user_msg"],
    )
    json_logger = runtime.context["json_logger"]
    
    if json_logger is not None:
        json_logger.log_retrieval_latency(
            query=state["last_user_msg"].content,
            stage="decomposition",
            latency=decomposition_latency,
        )
        if retrieval_tokens:
            json_logger.log_retrieval_tokens(
                query=state["last_user_msg"].content,
                token_usage=retrieval_tokens,
            )
    
    return {"sub_queries": result.sub_queries}


async def call_retrieve(state: GraphState, runtime: Runtime[RetrievalContext]) -> dict:
    """A node that invokes parallel retrieval based on subqueries."""
    if len(state["sub_queries"]) == 0:
        return {}
    
    # Choose a different collection for locomo benchmark
    collection = Collection.LOCOMO if os.getenv("FOR_LOCOMO") == "true" else Collection.ASSERTIONS
    
    retrieval_start = time.perf_counter()
    # Parallel mode
    if state["parallel_mode"]:
        results = await asyncio.gather(
            *[
                retrieve(query, collection, runtime)
                for query in state["sub_queries"]
            ]
        )
    # Sequential mode
    else:
        results  = [
            await retrieve(query, collection, runtime)
            for query in state["sub_queries"]
        ]
    retrieval_latency = time.perf_counter() - retrieval_start

    # Aggregate and deduplicate memories
    all_memories: dict[str, MemoryEntry] = {}
    for _, memories in results:
        for memory in memories:
            all_memories[memory.id] = memory
    
    memories_list = list(all_memories.values())
    get_console().print_memories(memories_list)

    # Log concurrent retrieval latency
    json_logger = runtime.context["json_logger"]
    if json_logger is not None:
        json_logger.log_retrieval_latency(
            query=state["last_user_msg"].content,
            stage="concurrent_retrieval",
            latency=retrieval_latency,
        )

    return {"memories": memories_list}
