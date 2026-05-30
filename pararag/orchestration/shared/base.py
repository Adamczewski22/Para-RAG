from abc import ABC, abstractmethod
from datetime import datetime

from pararag.shared.models import MemoryEntry, AssistantMessage, UserMessage, Message
from pararag.orchestration.shared.types import RetrievalContext, UpdateContext
from pararag.memory.services.memory_retrieval_service import MemoryRetrievalService
from pararag.memory.services.memory_update_service import MemoryUpdateService


class MemoryOrchestrator(ABC):
    """The core interface for a memory orchestrator. Governs LLM pipelines and exposes a unified memory API"""
    def __init__(self, update_service: MemoryUpdateService, retrieval_service: MemoryRetrievalService):
        self.conversation_history: list[Message] = []
        self.update_service = update_service
        self.retrieval_service = retrieval_service

    @abstractmethod
    async def add_user_msg(self, user_msg: UserMessage, timestamp: datetime) -> None:
        """Updates memory based on user's message"""
        pass
    
    @abstractmethod
    async def add_assistant_msg(self, assistant_msg: AssistantMessage, timestamp: datetime) -> None:
        """Updates memory based on assistant's message"""
        pass

    @abstractmethod
    async def retrieve(self, user_msg: UserMessage) -> list[MemoryEntry]:
        """Retrieves relevant memories for answering a user message as an aid to a chatbot assistant"""
        pass


class BaseMemoryOrchestrator(MemoryOrchestrator):
    """The base implementation of memory orchestrator shared by different implementations. 
    The internal implementation is configured via update and retrieve_graph and update_graph modules which define the required functionalities"""
    # Those class variables must be set to appropriate modules in concrete implemenations
    update_graph = None
    retrieval_graph = None

    CONVERSATION_WINDOW = 10 # Does not restrict the overall memory. Serves as context to the LLM pipeline.

    async def add_user_msg(self, user_msg: UserMessage, timestamp: datetime) -> None:
        """Extracts relevant facts from user message, and stores them in memory"""
        graph = self.update_graph.get_graph()
        graph_state = self.update_graph.init_graph_state(
            user_msg=user_msg, 
            conversation_history=self.conversation_history,
            timestamp=timestamp,
        )

        await graph.ainvoke(
            input=graph_state,
            context=UpdateContext(update_service=self.update_service)
        )

        self.conversation_history.append(user_msg)
        self.conversation_history = self.conversation_history[-self.CONVERSATION_WINDOW:]
    

    async def add_assistant_msg(self, assistant_msg: AssistantMessage, timestamp: datetime) -> None:
        """Adds assistant message to the converstation history"""
        self.conversation_history.append(assistant_msg)
        self.conversation_history = self.conversation_history[-self.CONVERSATION_WINDOW:]


    async def retrieve(self, user_msg: UserMessage) -> list[MemoryEntry]:
        """Retrieves relevant memories for answering a user message as an aid to a chatbot assistant"""
        graph = self.retrieval_graph.get_graph()
        graph_state = self.retrieval_graph.init_graph_state(user_msg, self.conversation_history)

        result = await graph.ainvoke(
            input=graph_state,
            context=RetrievalContext(retrieval_service=self.retrieval_service)
        )

        return result["memories"]
