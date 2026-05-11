from abc import ABC, abstractmethod

from pararag.shared.types import Vector, Collection
from pararag.shared.models import MemoryEntry

class MemoryStore(ABC):
    "A generic interface for the underlying memory store (e.g., qdrant vector store)"

    @abstractmethod
    async def init_collections(self) -> None:
        """Creates all the collections if not present"""
        pass
    
    @abstractmethod
    async def clear_collection(self, collection: Collection) -> None:
        """Clears the collection from memory entries"""
        pass

    @abstractmethod
    async def insert(self, vector: Vector, memory_entry: MemoryEntry, collection: Collection) -> None:
        """Inserts a memory entry with payload indexed by a vector into a collection"""
        pass

    @abstractmethod
    async def search(self, vector: Vector, collection: Collection, k: int) -> list[MemoryEntry]:
        """Returns the top k most similar memory entries based on vector similarity"""
        pass