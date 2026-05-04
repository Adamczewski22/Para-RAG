from langchain_core.messages import HumanMessage, BaseMessage, SystemMessage
from pydantic import BaseModel, Field
from typing import TypedDict
import asyncio

from app.memory.services.memory_update_service import MemoryUpdateService
from app.memory.infrastructure.qdrant_adapter import QdrantAdapter
from app.orchestration.shared.prompts import EXTRACT_ASSERTIONS_PROMPT
from app.shared.types import Collection
from app.ai.embeddings import get_embedder
from app.ai.llm import get_llm


class GraphState(TypedDict):
    conversation_history: list[BaseMessage]
    conversation_history_str: str
    last_user_msg: HumanMessage
    assertions: list[str]

class Assertions(BaseModel):
    assertions: list[str] = Field(description="a list of atomic assertions extracted from the users message to be inserted into the conversational memory.")


async def extract_assertions(state: GraphState) -> dict:
    """Extracts assertions from the latest user message to be stored in the conversational memory."""
    llm = get_llm().with_structured_output(Assertions)

    prompt = EXTRACT_ASSERTIONS_PROMPT.format(
        conversation_history=state["conversation_history_str"],
        user_message=state["last_user_msg"].content,
    )

    result = await llm.ainvoke([SystemMessage(prompt)])
    return {"assertions": result.assertions}


async def update_memory(state: GraphState) -> dict:
    """Update the memory with assertions"""
    update_service = MemoryUpdateService(
        store=QdrantAdapter(),
        embedder=get_embedder(),
    )

    await asyncio.gather(
        *[
            update_service.update_memory_from_content(assertion, Collection.ASSERTIONS)
            for assertion in state["assertions"]
        ]
    )
    return {}
