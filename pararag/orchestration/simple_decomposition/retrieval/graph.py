from langgraph.graph.state import CompiledStateGraph
from langgraph.graph import StateGraph, START, END
from functools import lru_cache

from .nodes import GraphState, decompose_query, call_retrieve
from pararag.orchestration.shared.utils import messages_to_string
from pararag.shared.models import Message


@lru_cache(maxsize=1)
def get_graph() -> CompiledStateGraph:
    """Builds and returns the compiled graph"""
    graph_builder = StateGraph(GraphState)
    graph_builder.add_sequence([decompose_query, call_retrieve])
    graph_builder.add_edge(START, "decompose_query")
    graph_builder.add_edge("call_retrieve", END)
    
    return graph_builder.compile()


def init_graph_state(user_msg: Message, conversation_history: list[Message]) -> GraphState:
    return {
        "conversation_history": conversation_history,
        "conversation_history_str": messages_to_string(conversation_history),
        "last_user_msg": user_msg,
        "sub_queries": [],
        "memories": [],
    }
