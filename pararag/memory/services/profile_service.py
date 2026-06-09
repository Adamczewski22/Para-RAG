from pararag.shared.models import Profile
from pararag.memory.domain.interfaces import ProfileStore


class ProfileService:
    def __init__(self, store: ProfileStore, users: list[str], memory_id: str):
        self.store = store
        self.users = users
        self.memory_id = memory_id


    async def init_store(self) -> None:
        """Initializes the underlying profile store"""
        await self.store.init_store()


    async def init_profiles(self) -> None:
        """Initializes empty profiles for given users if absent"""
        await self.store.init_profiles(
            usernames=self.users,
            namespace=self.memory_id,
        )


    async def update_profile(self, new_profile: str, user: str) -> None:
        """Updates a user profile within a namespace"""
        await self.store.update_profile(
            new_profile=new_profile,
            user=user,
            namespace=self.memory_id,
        )


    async def get_profiles(self) -> list[Profile]:
        """Returns all profiles from the namespace"""
        return await self.store.get_profiles(namespace=self.memory_id)
