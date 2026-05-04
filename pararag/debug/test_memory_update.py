from datetime import datetime
import asyncio

from pararag.memory.services.memory_update_service import MemoryUpdateService
from pararag.memory.infrastructure.qdrant_adapter import QdrantAdapter
from pararag.ai.embeddings import get_embedder
from pararag.shared.types import Collection


async def main():
    qdrant = QdrantAdapter()
    await qdrant.init_collections()

    update_service = MemoryUpdateService(
        store=qdrant,
        embedder=get_embedder(),
    )

    while True:
        content = input("Memory: ")
        if content.strip().lower() == "exit":
            break

        await update_service.update_memory_from_content(content, Collection.ASSERTIONS)


asyncio.run(main())