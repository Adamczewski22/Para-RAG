from langchain_core.tools import tool
from langgraph.runtime import Runtime

from pararag.orchestration.shared.types import RetrievalContext
from pararag.shared.types import Collection


async def retrieve(query: str, runtime: Runtime[RetrievalContext]):
    """Retrieve relevant memories based on semantic search"""
    retrieval_service = runtime.context["retrieval_service"]
    
    memories = await retrieval_service.retrieve_dense(
        query=query,
        collection=Collection.ASSERTIONS,
    )

    memories_str = "\n".join([str(memory) for memory in memories])
    return memories_str, memories
