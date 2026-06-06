from langchain_core.embeddings import Embeddings

from pararag.memory.domain.interfaces import MemoryStore
from pararag.shared.models import MemoryEntry
from pararag.shared.types import Collection


class MemoryRetrievalService:
    def __init__(self, store: MemoryStore, namespace: str, embedder: Embeddings):
        self.store = store
        self.namespace = namespace
        self.embedder = embedder
    
    async def retrieve_dense(self, query: str, collection: Collection, k: int = 4) -> list[MemoryEntry]:
        """Performs dense search on the collection of the underlying memory store and returns top k memory entries"""
        embedding = await self.embedder.aembed_query(query)
        return await self.store.search(
            vector=embedding,
            namespace=self.namespace,
            collection=collection,
            k=k,
        )
