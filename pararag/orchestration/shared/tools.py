from langchain_core.tools import tool
from langgraph.runtime import Runtime

from pararag.orchestration.shared.types import RetrievalContext, UpdateContext
from pararag.shared.types import Collection
from dotenv import find_dotenv, load_dotenv
import os

load_dotenv(find_dotenv())


async def retrieve(query: str, collection: Collection, runtime: Runtime[RetrievalContext]):
    """Retrieve relevant memories based on semantic search"""
    retrieval_service = runtime.context["retrieval_service"]
    retrieval_count = os.getenv("RETRIEVAL_COUNT")
    
    memories = await retrieval_service.retrieve_dense(
        query=query,
        collection=collection,
        k=int(retrieval_count) if retrieval_count is not None else 4
    )

    memories_str = "\n".join([str(memory) for memory in memories])
    return memories_str, memories
