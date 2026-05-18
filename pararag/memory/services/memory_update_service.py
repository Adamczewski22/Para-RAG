from langchain_core.embeddings import Embeddings
from datetime import datetime
import uuid

from pararag.memory.domain.interfaces import MemoryStore
from pararag.shared.models import MemoryEntry
from pararag.shared.types import Collection


class MemoryUpdateService:
    def __init__(self, store: MemoryStore, namespace: str, embedder: Embeddings):
        self.store = store
        self.namespace = namespace
        self.embedder = embedder
    
    async def update_memory(self, memory_entry: MemoryEntry, collection: Collection):
        """Embeds the memory entry and inserts it into the underlying memory store"""
        embedding = await self.embedder.aembed_query(memory_entry.content)

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