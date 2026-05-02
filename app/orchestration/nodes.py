from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langgraph.prebuilt import ToolNode
from langgraph.graph import add_messages
from typing import TypedDict, Annotated, List
from pydantic import BaseModel, Field
from uuid import uuid4
import asyncio

from app.orchestration.prompts import QUERY_DECOMPOSITION_PROMPT
from app.orchestration.tools import retrieve
from app.shared.models import MemoryEntry
from app.ai.llm import get_llm


class GraphState(TypedDict):
    conversation_history: List[BaseMessage]
    conversation_history_str: str
    last_user_msg: HumanMessage
    sub_queries: list[str]
    memories: list[MemoryEntry]

class SubQueries(BaseModel):
    sub_queries: list[str] = Field(description="A list of simple, atomic sub-queries later used for semantic search.")


async def decompose_query(state: GraphState) -> dict:
    """A node that decomposes the user query into atomic sub-queries to be used for parallel retrieval"""
    llm = get_llm().with_structured_output(SubQueries)

    prompt = QUERY_DECOMPOSITION_PROMPT.format(
        conversation_history=state["conversation_history_str"],
        user_query=state["last_user_msg"].content,
    )

    result = await llm.ainvoke([SystemMessage(prompt)])
    return {"sub_queries": result.sub_queries}


async def call_retrieve(state: GraphState) -> dict:
    """A node that invokes parallel retrieval based on subqueries."""
    if len(state["sub_queries"]) == 0:
        return {}
    
    print(state["sub_queries"])
    
    results = await asyncio.gather(
        *[
            retrieve(query)
            for query in state["sub_queries"]
        ]
    )

    memories = []
    for _, memories in results:
        memories.extend(memories)

    return {"memories": memories}
