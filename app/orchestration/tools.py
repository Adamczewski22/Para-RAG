from langchain_core.tools import tool

from app.memory.services.memory_retrieval_service import MemoryRetrievalService
from app.memory.infrastructure.qdrant_adapter import QdrantAdapter
from app.shared.types import Collection
from app.ai.embeddings import get_embedder


@tool(response_format="content_and_artifact")
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
