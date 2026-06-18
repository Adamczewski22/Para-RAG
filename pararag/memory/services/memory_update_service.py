from langchain_core.embeddings import Embeddings
from datetime import datetime
import uuid

from pararag.memory.domain.interfaces import MemoryStore
from pararag.shared.models import MemoryEntry
from pararag.shared.types import Collection
from pararag.shared.logger import JsonLogger
from pararag.ai.embeddings import EMBEDDINGS_MODEL, count_embedding_tokens


class MemoryUpdateService:
    def __init__(
        self,
        store: MemoryStore,
        namespace: str,
        embedder: Embeddings,
        json_logger: JsonLogger | None = None,
    ):
        self.store = store
        self.namespace = namespace
        self.embedder = embedder
        self.json_logger = json_logger
    
    async def update_memory(self, memory_entry: MemoryEntry, collection: Collection):
        """Embeds the memory entry and inserts it into the underlying memory store"""
        embedding_tokens = count_embedding_tokens(memory_entry.content)
        embedding = await self.embedder.aembed_query(memory_entry.content)

        if self.json_logger is not None:
            self.json_logger.log_embedding_tokens(
                category="update",
                text=memory_entry.content,
                token_usage=embedding_tokens,
                model=EMBEDDINGS_MODEL,
                collection=collection.value,
            )

        await self.store.insert(
            vector=embedding,
            memory_entry=memory_entry,
            namespace=self.namespace,
            collection=collection,
        )
    
    async def update_memory_from_content(self, content: str, collection: Collection, timestamp: datetime):
        """Handles the intialization of memory entry, embeds it and inserts into the underlying memory store"""
        memory = MemoryEntry(
            id=str(uuid.uuid4()),
            content=content,
            date=timestamp,
        )
        await self.update_memory(memory, collection)
