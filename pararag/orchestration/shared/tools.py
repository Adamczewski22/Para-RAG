from langchain_core.tools import tool
from langgraph.runtime import Runtime

from pararag.orchestration.shared.types import RetrievalContext
from pararag.shared.types import Collection
from dotenv import find_dotenv, load_dotenv
import os

load_dotenv(find_dotenv())


async def retrieve(query: str, runtime: Runtime[RetrievalContext]):
    """Retrieve relevant memories based on semantic search"""
    retrieval_service = runtime.context["retrieval_service"]

    # Choose a different collection for locomo benchmark
    collection = Collection.LOCOMO if os.getenv("FOR_LOCOMO") == "true" else Collection.ASSERTIONS
    
    memories = await retrieval_service.retrieve_dense(
        query=query,
        collection=collection,
    )

    memories_str = "\n".join([str(memory) for memory in memories])
    return memories_str, memories
