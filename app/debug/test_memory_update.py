from datetime import datetime
import asyncio

from app.memory.services.memory_update_service import MemoryUpdateService
from app.memory.infrastructure.qdrant_adapter import QdrantAdapter
from app.ai.embeddings import get_embedder
from app.shared.models import MemoryEntry
from app.shared.types import Collection


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