from langchain_core.embeddings import Embeddings

from app.memory.domain.interfaces import MemoryStore
from app.shared.models import MemoryEntry
from app.shared.types import Collection


class MemoryUpdateService:
    def __init__(self, store: MemoryStore, embedder: Embeddings):
        self.store = store
        self.embedder = embedder
    
    async def update_memory(self, memory_entry: MemoryEntry, collection: Collection):
        """Embeds the memory entry and inserts it into the underlying memory store"""
        embedding = await self.embedder.aembed_query(memory_entry.content)

        await self.store.insert(
            vector=embedding,
            memory_entry=memory_entry,
            collection=collection,
        )
