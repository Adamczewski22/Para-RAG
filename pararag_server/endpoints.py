from fastapi import FastAPI, HTTPException, status, Depends
from contextlib import asynccontextmanager
from typing import Annotated
import logging
import asyncio

from pararag import ParaRAGMemory
from pararag_server.schemas import ClearCollectionRequest, MessagesRequest, RetrieveRequest, RetrieveResponse, MemorySelector


log = logging.getLogger("ParaRAG")


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        log.info("Intitializing memory store")
        memory = ParaRAGMemory()

        # Initialize memory store with a retry loop
        max_memory_store_attempts = 10
        delay = 1
        for i in range(max_memory_store_attempts):
            await asyncio.sleep(delay)
            try:
                await memory.init_memory_store()
                break
            except Exception:
                if i < max_memory_store_attempts - 1:
                    log.warning("Failed to initialize memory store. Retrying...")
                else:
                    raise

    except Exception:
        log.critical(f"Failed to initialize memory store", exc_info=True)
        raise

    try:
        log.info("Server startup succesful")
        yield
    finally:
        log.info("Server shutting down")
    

app = FastAPI(
    title="ParaRAG server",
    lifespan=lifespan,
)


def create_memory(request: MemorySelector) -> ParaRAGMemory:
    """Dependency for creating memory instance"""
    try:
        return ParaRAGMemory(
            memory_id=request.memory_id,
            memory_version=request.memory_version,
        )
    except Exception:
        log.exception("Failed to create ParaRAGMemory")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Failed to create ParaRAGMemory"
        )


@app.post(
    "/messages", 
    status_code=status.HTTP_204_NO_CONTENT
)
async def add_message(
    request: MessagesRequest, 
    memory: Annotated[ParaRAGMemory, Depends(create_memory)]
) -> None:
    """Updates memory based on the message"""
    try:
        if request.message_type == "user":
            await memory.add_user_msg(
                user_msg=request.content,
                speaker=request.speaker,
                timestamp=request.timestamp,
            )
        elif request.message_type == "assistant":
            await memory.add_assistant_msg(
                assistant_msg=request.content,
                timestamp=request.timestamp,
            )
    
    except Exception:
        log.exception("Failed to add message to memory")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Failed to add message to memory"
        )


@app.post(
    "/retrieve",
    response_model=RetrieveResponse,
    status_code=status.HTTP_200_OK,
)
async def retrieve_memories(
    request: RetrieveRequest,
    memory: Annotated[ParaRAGMemory, Depends(create_memory)]
) -> RetrieveResponse:
    """Retrieves relevant memories for answering a user message as an aid to a chatbot assistant"""
    try:
        memories = await memory.retrieve_memories(user_msg=request.user_msg)
    except Exception:
        log.exception("Failed to retrieve memories")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Failed to retrieve memories"
        )

    return RetrieveResponse(memories=memories)


@app.delete(
    "/collections",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def clear_collection(
    request: ClearCollectionRequest,
    memory: Annotated[ParaRAGMemory, Depends(create_memory)]
) -> None:
    try:
        await memory.clear_collection(memory_collection=request.collection)
    except Exception:
        log.exception("Failed to clear collections")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Failed to clear collections"
        )
