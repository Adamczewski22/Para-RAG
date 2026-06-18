from dotenv import find_dotenv, load_dotenv
from datetime import datetime
import os

from pararag.orchestration import MemoryVersion, MemoryOrchestrator, create_memory_orchestrator
from pararag.shared.models import MemoryEntry, UserMessage, AssistantMessage, Profile
from pararag.shared.types import Collection
from pararag.shared.logger import JsonLogger
from pararag.memory.infrastructure.qdrant_adapter import QdrantAdapter
from pararag.memory.infrastructure.sqlite_adapter import SqliteAdapter
from pararag.memory.domain.interfaces import MemoryStore, ProfileStore
from pararag.memory.services.memory_update_service import MemoryUpdateService
from pararag.memory.services.memory_retrieval_service import MemoryRetrievalService
from pararag.memory.services.memory_admin_service import MemoryAdminService
from pararag.memory.services.profile_service import ProfileService
from pararag.ai.embeddings import get_embedder


load_dotenv(find_dotenv())

DEFAULT_MEMORY_VERSION = MemoryVersion.SIMPLE_DECOMPOSITION


class ParaRAGMemory:
    """The ParaRAG framework facade implementing conversational memory"""
    def __init__(
            self,
            memory_id: str = "main",
            memory_version: MemoryVersion | None = None, 
            memory_store: MemoryStore | None = None,
            profile_store: ProfileStore | None = None,
            json_logger: JsonLogger | None = None,
            users: list[str] = ["User"],
    ):
        # If stores were not specified, use defaults
        self.memory_store = memory_store if memory_store else QdrantAdapter()
        self.profile_store = profile_store if profile_store else SqliteAdapter()
        self.memory_id = memory_id
        self.memory_version = memory_version

        # Init the memory admin service
        self.memory_admin_service = MemoryAdminService(store=self.memory_store, namespace=self.memory_id)

        # Init update service
        embedder = get_embedder()

        memory_update_service = MemoryUpdateService(
            store=self.memory_store,
            namespace=self.memory_id,
            embedder=embedder,
            json_logger=json_logger,
        )

        # Init retrieval service
        memory_retrieval_service = MemoryRetrievalService(
            store=self.memory_store,
            namespace=memory_id,
            embedder=embedder,
            json_logger=json_logger,
        )

        # Init profile service
        profile_service = ProfileService(store=self.profile_store, users=users, memory_id=memory_id)
        self.profile_service = profile_service

        # Set memory version
        memory_version = memory_version if memory_version else DEFAULT_MEMORY_VERSION

        # Create memory orchestrator, injecting the services
        self.orchestrator: MemoryOrchestrator = create_memory_orchestrator(
            version=memory_version,
            update_service=memory_update_service,
            retrieval_service=memory_retrieval_service,
            profile_service=profile_service,
            json_logger=json_logger,
            users=users,
        )

    async def retrieve_memories(
        self, 
        user_msg: str
    ) -> list[MemoryEntry]:
        """Retrieves relevant memories for answering a user message as an aid to a chatbot assistant"""
        user_msg_obj = UserMessage(content=user_msg)
        return await self.orchestrator.retrieve(user_msg_obj)
    
    
    async def retrieve_user_profiles(self) -> list[Profile]:
        """Get all user profiles"""
        if self.memory_version in [MemoryVersion.SIMPLE_DECOMPOSITION, MemoryVersion.DEDUPLICATION]:
            return []

        return await self.profile_service.get_profiles()


    async def force_profile_update(self, msg_id: str | None = None) -> None:
        """Force profile memory to update from buffered deduplicated assertions."""
        force_profile_update = getattr(self.orchestrator, "force_profile_update", None)
        if force_profile_update is not None:
            await force_profile_update(msg_id=msg_id)


    async def add_conversation_turn(
        self, 
        user_msg: str, 
        assistant_msg: str, 
        timestamp: datetime | None = None
    ) -> None:
        """Updates memory based on one conversation turn: user messages followed by an assistant message"""
        # Timestamp defaults to current datetime
        timestamp = timestamp if timestamp else datetime.now()
        await self.add_user_msg(user_msg=user_msg, timestamp=timestamp)
        await self.add_assistant_msg(assistant_msg=assistant_msg, timestamp=timestamp)
    

    async def add_user_msg(
        self, 
        user_msg: str, 
        speaker: str | None = None, 
        timestamp: datetime | None = None, 
        msg_id: str | None = None,
        assertions: list[str] | None = None,
        deduplicated_assertions: list[str] | None = None,
    ) -> None:
        """Updates memory based on user's message"""
        # Speaker defaults to "user" if not present
        if speaker is None:
            user_msg_obj = UserMessage(content=user_msg)
        else:
            user_msg_obj = UserMessage(speaker=speaker, content=user_msg)

        await self.orchestrator.add_user_msg(
            user_msg=user_msg_obj, 
            timestamp=timestamp if timestamp else datetime.now(), # timestamp defaults to current datetime
            msg_id=msg_id,
            assertions=assertions,
            deduplicated_assertions=deduplicated_assertions,
        )
    

    async def add_assistant_msg(
        self, 
        assistant_msg: str, 
        timestamp: datetime | None = None
    ) -> None:
        """Updates memory based on assistant's message"""
        assistant_msg_obj = AssistantMessage(content=assistant_msg)

        await self.orchestrator.add_assistant_msg(
            assistant_msg=assistant_msg_obj,
            timestamp=timestamp if timestamp else datetime.now(), # timestamp defaults to current datetime
        )


    async def init_memory_store(self) -> None:
        """Initializes the underlying memory store"""
        await self.memory_admin_service.init_memory()

    
    async def init_profile_store(self) -> None:
        """Initializes the underlying profile store"""
        await self.profile_service.init_store()
        await self.profile_service.init_profiles()


    async def delete_profiles(self) -> None:
        """Deletes all profiles from the namespace"""
        await self.profile_service.delete_profiles()
    

    async def clear_collection(
        self, 
        memory_collection: Collection | None = None
    ) -> None:
        """Deletes all data points from a collection"""
        default_collection = Collection.LOCOMO if os.getenv("FOR_LOCOMO") == "true" else Collection.ASSERTIONS
        collection = memory_collection if memory_collection is not None else default_collection

        await self.memory_admin_service.clear_collection(collection)
