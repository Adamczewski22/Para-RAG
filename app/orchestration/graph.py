from langchain_core.messages import BaseMessage
from langgraph.graph.state import CompiledStateGraph
from langgraph.graph import StateGraph
from functools import lru_cache

from app.orchestration.nodes import GraphState, decompose_query, call_retrieve
from app.orchestration.utils import messages_to_string


@lru_cache(maxsize=1)
def get_graph() -> CompiledStateGraph:
    """Builds and returns the compiled graph"""
    graph_builder = StateGraph(GraphState)
    graph_builder.add_sequence([decompose_query, call_retrieve])
    
    return graph_builder.compile()


def init_graph_state(messages: list[BaseMessage]) -> GraphState:
    return {
        "conversation_history": messages,
        "conversation_history_str": messages_to_string(messages),
        "last_user_msg": messages[-1],
        "sub_queries": [],
        "memories": [],
    }