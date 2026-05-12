from langgraph.graph.state import CompiledStateGraph
from langgraph.graph import StateGraph, START, END
from datetime import datetime
from functools import lru_cache

from pararag.orchestration.shared.utils import messages_to_string
from pararag.orchestration.shared.types import UpdateContext
from pararag.shared.models import Message
from .nodes import GraphState, extract_assertions, update_memory


@lru_cache(maxsize=1)
def get_graph() -> CompiledStateGraph:
    graph_builder = StateGraph(state_schema=GraphState, context_schema=UpdateContext)
    graph_builder.add_sequence([extract_assertions, update_memory])
    graph_builder.add_edge(START, "extract_assertions")
    graph_builder.add_edge("update_memory", END)
    
    return graph_builder.compile()


def init_graph_state(user_msg: Message, conversation_history: list[Message], timestamp: datetime) -> GraphState:
    return {
        "conversation_history": conversation_history,
        "conversation_history_str": messages_to_string(conversation_history),
        "last_user_msg": user_msg,
        "timestamp": timestamp,
        "assertions": [],
    }