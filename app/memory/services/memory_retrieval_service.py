from langchain_core.embeddings import Embeddings

from app.memory.domain.interfaces import MemoryStore
from app.shared.models import MemoryEntry
from app.shared.types import Collection


class MemoryRetrievalService:
    def __init__(self, store: MemoryStore, embedder: Embeddings):
        self.store = store
        self.embedder = embedder
    
    async def retrieve_dense(self, query: str, collection: Collection, k: int = 4) -> list[MemoryEntry]:
        """Performs dense search on the collection of the underlying memory store and returns top k memory entries"""
        embedding = await self.embedder.aembed_query(query)
        return await self.store.search(
            vector=embedding,
            collection=collection,
            k=k,
        )