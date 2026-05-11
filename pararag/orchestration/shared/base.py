from abc import ABC, abstractmethod

from pararag.shared.models import MemoryEntry, AssistantMessage, UserMessage, Message
from pararag.memory.services.memory_retrieval_service import MemoryRetrievalService
from pararag.memory.services.memory_update_service import MemoryUpdateService


class MemoryOrchestrator(ABC):
    """The core interface for a memory orchestrator. Governs LLM pipelines and exposes a unified memory API"""
    def __init__(self, update_service: MemoryUpdateService, retrieval_service: MemoryRetrievalService):
        self.conversation_history: list[Message] = []
        self.update_service = update_service
        self.retrieval_service = retrieval_service

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
