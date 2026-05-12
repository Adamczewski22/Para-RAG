from dotenv import find_dotenv, load_dotenv
from datetime import datetime
import os

from pararag.orchestration import MemoryVersion, MemoryOrchestrator, create_memory_orchestrator
from pararag.shared.models import MemoryEntry, UserMessage, AssistantMessage
from pararag.shared.types import Collection
from pararag.memory.infrastructure.qdrant_adapter import QdrantAdapter
from pararag.memory.domain.interfaces import MemoryStore
from pararag.memory.services.memory_update_service import MemoryUpdateService
from pararag.memory.services.memory_retrieval_service import MemoryRetrievalService
from pararag.memory.services.memory_admin_service import MemoryAdminService
from pararag.ai.embeddings import get_embedder

load_dotenv(find_dotenv())

DEFAULT_MEMORY_VERSION = MemoryVersion.SIMPLE_DECOMPOSITION


class ParaRAGMemory:
    """The ParaRAG framework facade implementing conversational memory"""
    def __init__(
            self, 
            memory_version: MemoryVersion = DEFAULT_MEMORY_VERSION, 
            memory_store: MemoryStore | None = None,
        ):
        # If memory store was not specified, use the default one
        self.memory_store = memory_store if memory_store else QdrantAdapter()

        # Init the memory admin service
        self.memory_admin_service = MemoryAdminService(self.memory_store)

        # Init retrieval and update services and inject them into the memory orchestrator
        embedder = get_embedder()
        memory_update_service = MemoryUpdateService(store=self.memory_store, embedder=embedder)
        memory_retrieval_service = MemoryRetrievalService(store=self.memory_store, embedder=embedder)

        self.orchestrator: MemoryOrchestrator = create_memory_orchestrator(
            version=memory_version,
            update_service=memory_update_service,
            retrieval_service=memory_retrieval_service,
        )


    async def retrieve_memories(self, user_msg: str) -> list[MemoryEntry]:
        """Retrieves relevant memories for answering a user message as an aid to a chatbot assistant"""
        user_msg_obj = UserMessage(content=user_msg)
        return await self.orchestrator.retrieve(user_msg_obj)


    async def add_conversation_turn(self, user_msg: str, assistant_msg: str, timestamp: datetime | None = None) -> None:
        """Updates memory based on one conversation turn: user messages followed by an assistant message"""
        # Timestamp defaults to current datetime
        timestamp = timestamp if timestamp else datetime.now()
        await self.add_user_msg(user_msg=user_msg, timestamp=timestamp)
        await self.add_assistant_msg(assistant_msg=assistant_msg, timestamp=timestamp)
    

    async def add_user_msg(self, user_msg: str, speaker: str | None = None, timestamp: datetime | None = None) -> None:
        """Updates memory based on user's message"""
        # Speaker defaults to "user" if not present
        if speaker is None:
            user_msg_obj = UserMessage(content=user_msg)
        else:
            user_msg_obj = UserMessage(speaker=speaker, content=user_msg)

        await self.orchestrator.add_user_msg(
            user_msg=user_msg_obj, 
            timestamp=timestamp if timestamp else datetime.now(), # timestamp defaults to current datetime
        )
    

    async def add_assistant_msg(self, assistant_msg: str, timestamp: datetime | None = None) -> None:
        """Updates memory based on assistant's message"""
        assistant_msg_obj = AssistantMessage(content=assistant_msg)

        await self.orchestrator.add_assistant_msg(
            assistant_msg=assistant_msg_obj,
            timestamp=timestamp if timestamp else datetime.now(), # timestamp defaults to current datetime
        )


    async def init_memory_store(self) -> None:
        """Initializes the underlying memory store"""
        await self.memory_admin_service.init_memory()
    

    async def clear_collection(self, memory_collection: Collection | None = None) -> None:
        """Deletes all data points from a collection"""
        default_collection = Collection.LOCOMO if os.getenv("FOR_LOCOMO") == "true" else Collection.ASSERTIONS
        collection = memory_collection if memory_collection is not None else default_collection

        await self.memory_admin_service.clear_collection(collection)
