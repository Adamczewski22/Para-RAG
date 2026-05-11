from pararag.memory.domain.interfaces import MemoryStore
from pararag.shared.types import Collection

class MemoryAdminService:
    def __init__(self, store: MemoryStore):
        self.store = store
    
    async def init_memory(self):
        """Initializes the underlying memory store"""
        await self.store.init_collections()
    
    async def clear_collection(self, collection: Collection):
        """Deletes all data points from a collection"""
        await self.store.clear_collection(collection)
