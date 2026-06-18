from langchain_core.embeddings import Embeddings

from pararag.memory.domain.interfaces import MemoryStore
from pararag.shared.models import MemoryEntry
from pararag.shared.types import Collection
from pararag.shared.logger import JsonLogger
from pararag.ai.embeddings import EMBEDDINGS_MODEL, count_embedding_tokens


class MemoryRetrievalService:
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
    
    async def retrieve_dense(
        self,
        query: str,
        collection: Collection,
        k: int = 4,
        embedding_category: str = "retrieval",
    ) -> list[MemoryEntry]:
        """Performs dense search on the collection of the underlying memory store and returns top k memory entries"""
        embedding_tokens = count_embedding_tokens(query)
        embedding = await self.embedder.aembed_query(query)

        if self.json_logger is not None:
            self.json_logger.log_embedding_tokens(
                category=embedding_category,
                text=query,
                token_usage=embedding_tokens,
                model=EMBEDDINGS_MODEL,
                collection=collection.value,
            )

        return await self.store.search(
            vector=embedding,
            namespace=self.namespace,
            collection=collection,
            k=k,
        )
