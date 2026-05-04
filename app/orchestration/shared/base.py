from langchain_core.messages import AIMessage, HumanMessage
from abc import ABC, abstractmethod

from app.shared.models import MemoryEntry


class MemoryOrchestrator(ABC):
    """The core interface for a memory orchestrator. Governs LLM pipelines and exposes a unified memory API"""

    @abstractmethod
    async def add_user_msg(self, user_msg: HumanMessage) -> None:
        """Updates memory based on user's message"""
        pass
    
    @abstractmethod
    async def add_assistant_msg(self, assistant_msg: AIMessage) -> None:
        """Updates memory based on assistant's message"""
        pass

    @abstractmethod
    async def retrieve(self, user_msg: HumanMessage) -> list[MemoryEntry]:
        """Retrieves relevant memories for answering a user message as an aid to a chatbot assistant"""
        pass
