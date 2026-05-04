from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from dotenv import load_dotenv, find_dotenv

from app.orchestration.shared.base import MemoryOrchestrator
from app.shared.models import MemoryEntry
from .retrieval import graph as retrieval_graph
from .update import graph as update_graph

load_dotenv(find_dotenv())

CONVERSATION_WINDOW = 10 # Does not restrict the overall memory. Serves as context to the LLM pipeline.


class SimpleDecompositionMemory(MemoryOrchestrator):
    def __init__(self):
        self.conversation_history: list[BaseMessage] = []
    

    async def add_user_msg(self, user_msg: HumanMessage) -> None:
        """Extracts relevant facts from user message, and stores them in memory"""
        graph = update_graph.get_graph()
        graph_state = update_graph.init_graph_state(user_msg, self.conversation_history)
        await graph.ainvoke(input=graph_state)

        self.conversation_history.append(user_msg)
        self.conversation_history = self.conversation_history[-CONVERSATION_WINDOW:]
    

    async def add_assistant_msg(self, assistant_msg: AIMessage) -> None:
        """Adds assistant message to the converstation history"""
        self.conversation_history.append(assistant_msg)
        self.conversation_history = self.conversation_history[-CONVERSATION_WINDOW:]


    async def retrieve(self, user_msg: HumanMessage) -> list[MemoryEntry]:
        """Retrieves relevant memories for answering a user message as an aid to a chatbot assistant"""
        graph = retrieval_graph.get_graph()
        graph_state = retrieval_graph.init_graph_state(user_msg, self.conversation_history)
        
        result = await graph.ainvoke(input=graph_state)
        return result["memories"]
