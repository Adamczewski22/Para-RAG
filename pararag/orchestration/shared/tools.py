from langchain_core.tools import tool

from pararag.memory.services.memory_retrieval_service import MemoryRetrievalService
from pararag.memory.infrastructure.qdrant_adapter import QdrantAdapter
from pararag.shared.types import Collection
from pararag.ai.embeddings import get_embedder


async def retrieve(query: str):
    """Retrieve relevant memories based on semantic search"""
    store = QdrantAdapter()
    embedder = get_embedder()
    retrieval_service = MemoryRetrievalService(store, embedder)

    memories = await retrieval_service.retrieve_dense(
        query=query,
        collection=Collection.ASSERTIONS,
    )

    memories_str = "\n".join([str(memory) for memory in memories])
    return memories_str, memories
