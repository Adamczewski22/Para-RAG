from langchain_core.messages import HumanMessage, BaseMessage
from langgraph.graph.state import CompiledStateGraph
from langgraph.graph import StateGraph, START, END
from functools import lru_cache

from app.orchestration.shared.utils import messages_to_string
from .nodes import GraphState, extract_assertions, update_memory


@lru_cache(maxsize=1)
def get_graph() -> CompiledStateGraph:
    graph_builder = StateGraph(GraphState)
    graph_builder.add_sequence([extract_assertions, update_memory])
    graph_builder.add_edge(START, "extract_assertions")
    graph_builder.add_edge("update_memory", END)
    
    return graph_builder.compile()


def init_graph_state(user_msg: HumanMessage, conversation_history: list[BaseMessage]) -> GraphState:
    return {
        "conversation_history": conversation_history,
        "conversation_history_str": messages_to_string(conversation_history),
        "last_user_msg": user_msg,
        "assertions": []
    }