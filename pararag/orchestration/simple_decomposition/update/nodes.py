from langchain_core.messages import SystemMessage
from pydantic import BaseModel, Field
from typing import TypedDict
from dotenv import load_dotenv, find_dotenv
import asyncio
import os

from pararag.memory.services.memory_update_service import MemoryUpdateService
from pararag.memory.infrastructure.qdrant_adapter import QdrantAdapter
from pararag.orchestration.shared.prompts import EXTRACT_ASSERTIONS_PROMPT, LOCOMO_EXTRACT_ASSERTIONS_PROMPT
from pararag.shared.types import Collection
from pararag.shared.models import Message
from pararag.ai.embeddings import get_embedder
from pararag.ai.llm import get_llm
from pararag.shared.console import get_console

load_dotenv(find_dotenv())


class GraphState(TypedDict):
    conversation_history: list[Message]
    conversation_history_str: str
    last_user_msg: Message
    assertions: list[str]

class Assertions(BaseModel):
    assertions: list[str] = Field(description="a list of atomic assertions extracted from the users message to be inserted into the conversational memory.")


async def extract_assertions(state: GraphState) -> dict:
    """Extracts assertions from the latest user message to be stored in the conversational memory."""
    llm = get_llm().with_structured_output(Assertions)

    # Prompt suited for locomo evaluation: assertion extraction for conversation
    if os.getenv("FOR_LOCOMO") == "true":
        prompt = LOCOMO_EXTRACT_ASSERTIONS_PROMPT.format(
            conversation_history=state["conversation_history_str"],
            user_message=str(state["last_user_msg"]),
        )
    # Prompt suited for main use case: assertion extraction for user/assstant conversation.
    else:
        prompt = EXTRACT_ASSERTIONS_PROMPT.format(
            conversation_history=state["conversation_history_str"],
            user_message=str(state["last_user_msg"]),
        )

    result = await llm.ainvoke([SystemMessage(prompt)])
    get_console().print_assertions(result.assertions)
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
