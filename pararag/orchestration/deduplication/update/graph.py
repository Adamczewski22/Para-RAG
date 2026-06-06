from langgraph.graph.state import CompiledStateGraph
from langgraph.graph import StateGraph, START, END
from datetime import datetime
from functools import lru_cache

from pararag.shared.models import Message
from pararag.orchestration.simple_decomposition.update.nodes import extract_assertions
from pararag.orchestration.simple_decomposition.update.graph import init_graph_state as init_graph_state_sd
from pararag.orchestration.shared.types import MemoryContext
from .nodes import update_memory, DeduplicationState


@lru_cache(maxsize=1)
def get_graph() -> CompiledStateGraph:
    graph_builder = StateGraph(state_schema=DeduplicationState, context_schema=MemoryContext)
    graph_builder.add_sequence([extract_assertions, update_memory])
    graph_builder.add_edge(START, "extract_assertions")
    graph_builder.add_edge("update_memory", END)

    return graph_builder.compile()


def init_graph_state(
    user_msg: Message, 
    conversation_history: list[Message], 
    timestamp: datetime, 
    msg_id: str | None = None
) -> DeduplicationState:
    # Deduplication memory adds some extra fields to simple decomposition memory graph state
    state = init_graph_state_sd(user_msg, conversation_history, timestamp, msg_id)
    state["update_decisions"] = []
    state["deduplicated_assertions"] = []
    return state
