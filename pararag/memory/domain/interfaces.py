from abc import ABC, abstractmethod
from pathlib import Path

from pararag.shared.types import Vector, Collection
from pararag.shared.models import MemoryEntry, Profile

class MemoryStore(ABC):
    "A generic interface for the underlying memory store (e.g., qdrant vector store)"

    @abstractmethod
    async def init_collections(self) -> None:
        """Creates all the collections if not present"""
        pass
    
    @abstractmethod
    async def clear_collection(self, namespace: str, collection: Collection) -> None:
        """Clears the collection from memory entries"""
        pass

    @abstractmethod
    async def insert(self, vector: Vector, memory_entry: MemoryEntry, namespace: str, collection: Collection) -> None:
        """Inserts a memory entry with payload indexed by a vector into a collection"""
        pass

    @abstractmethod
    async def search(self, vector: Vector, namespace: str, collection: Collection, k: int) -> list[MemoryEntry]:
        """Returns the top k most similar memory entries based on vector similarity"""
        pass


class ProfileStore(ABC):
    "A generic interace for a database of user profiles (e.g., sqlite)"
    def __init__(self, db_path: Path | None = None):
        self.db_path = db_path
    
    @abstractmethod 
    async def init_store(self) -> None:
        """Initializes the whole profile store"""

    @abstractmethod
    async def init_profiles(self, usernames: list[str], namespace: str) -> None:
        """Initializes empty profiles for given users if absent"""
        pass
        
    @abstractmethod
    async def update_profile(self, new_profile: str, user: str, namespace: str) -> None:
        """Updates a user profile within a namespace"""
        pass

    @abstractmethod
    async def get_profiles(self, namespace: str) -> list[Profile]:
        """Returns all profiles from the namespace"""
        pass
