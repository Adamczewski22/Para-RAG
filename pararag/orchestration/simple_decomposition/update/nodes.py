from langchain_core.messages import SystemMessage
from langgraph.runtime import Runtime
from dotenv import load_dotenv, find_dotenv
from datetime import datetime
from pydantic import BaseModel, Field
from typing import TypedDict
import asyncio
import os

from pararag.orchestration.shared.prompts import EXTRACT_ASSERTIONS_PROMPT, LOCOMO_EXTRACT_ASSERTIONS_PROMPT
from pararag.orchestration.shared.types import UpdateContext
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
    timestamp: datetime
    assertions: list[str]
    msg_id: str

class Assertions(BaseModel):
    assertions: list[str] = Field(description="a list of atomic assertions extracted from the users message to be inserted into the conversational memory.")


async def extract_assertions(state: GraphState, runtime: Runtime[UpdateContext]) -> dict:
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

    # Extract assertions
    result = await llm.ainvoke([SystemMessage(prompt)])

    # Logs
    get_console().print_assertions(result.assertions)
    json_logger = runtime.context["json_logger"]

    if state["msg_id"] is not None:
        json_logger.log_extraction(
            msg_id=state["msg_id"],
            assertions=result.assertions,
        )

    return {"assertions": result.assertions}


async def update_memory(state: GraphState, runtime: Runtime[UpdateContext]) -> dict:
    """Update the memory with assertions"""
    update_service = runtime.context["update_service"]

    # Choose a different collection for locomo benchmark
    collection = Collection.LOCOMO if os.getenv("FOR_LOCOMO") == "true" else Collection.ASSERTIONS

    await asyncio.gather(
        *[
            update_service.update_memory_from_content(
                content=assertion, 
                collection=collection,
                timestamp=state["timestamp"],
            )
            for assertion in state["assertions"]
        ]
    )
    return {}
