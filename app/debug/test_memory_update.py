from datetime import datetime
import asyncio

from app.memory.services.memory_update_service import MemoryUpdateService
from app.memory.infrastructure.qdrant_adapter import QdrantAdapter
from app.ai.embeddings import get_embedder
from app.shared.models import MemoryEntry
from app.shared.types import Collection


memory = MemoryEntry(
    content="User likes cats very much",
    date=datetime.now()
)

async def main():
    qdrant = QdrantAdapter()
    await qdrant.init_collections()

    update_service = MemoryUpdateService(
        store=qdrant,
        embedder=get_embedder(),
    )

    await update_service.update_memory(
        memory_entry=memory,
        collection=Collection.ASSERTIONS,
    )

asyncio.run(main())