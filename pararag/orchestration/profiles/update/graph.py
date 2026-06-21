from langgraph.graph.state import CompiledStateGraph
from langgraph.graph import StateGraph, START, END
from functools import lru_cache
from datetime import datetime

from pararag.shared.models import Message, Profile
from pararag.orchestration.shared.types import ProfileUpdateContext
from pararag.orchestration.simple_decomposition.update.nodes import extract_assertions
from pararag.orchestration.deduplication.update.nodes import update_memory
from pararag.orchestration.deduplication.update.graph import init_graph_state as init_graph_state_dp
from .nodes import ProfileState


@lru_cache(maxsize=1)
def get_graph() -> CompiledStateGraph:
    graph_builder = StateGraph(state_schema=ProfileState, context_schema=ProfileUpdateContext)
    graph_builder.add_sequence([extract_assertions, update_memory])
    graph_builder.add_edge(START, "extract_assertions")
    graph_builder.add_edge("update_memory", END)

    return graph_builder.compile()


def init_graph_state(
    user_msg: Message, 
    conversation_history: list[Message], 
    timestamp: datetime, 
    msg_id: str | None = None,
    parallel_mode: bool = True,
    assertions: list[str] | None = None,
    deduplicated_assertions: list[str] | None = None,
    users: list[str] = [],
) -> StateGraph:
    # Profile memory state extends deduplication memory state
    state = init_graph_state_dp(
        user_msg=user_msg,
        conversation_history=conversation_history,
        timestamp=timestamp,
        msg_id=msg_id,
        assertions=assertions,
        deduplicated_assertions=deduplicated_assertions,
        parallel_mode=parallel_mode,
    )

    state["users"] = users
    return state
