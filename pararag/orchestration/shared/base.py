from abc import ABC, abstractmethod

from pararag.shared.models import MemoryEntry, AssistantMessage, UserMessage


class MemoryOrchestrator(ABC):
    """The core interface for a memory orchestrator. Governs LLM pipelines and exposes a unified memory API"""

    @abstractmethod
    async def add_user_msg(self, user_msg: UserMessage) -> None:
        """Updates memory based on user's message"""
        pass
    
    @abstractmethod
    async def add_assistant_msg(self, assistant_msg: AssistantMessage) -> None:
        """Updates memory based on assistant's message"""
        pass

    @abstractmethod
    async def retrieve(self, user_msg: UserMessage) -> list[MemoryEntry]:
        """Retrieves relevant memories for answering a user message as an aid to a chatbot assistant"""
        pass
