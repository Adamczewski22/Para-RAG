from dotenv import find_dotenv, load_dotenv
from pathlib import Path
import aiosqlite
import os

from pararag.shared.models import Profile
from pararag.memory.domain.interfaces import ProfileStore


load_dotenv(find_dotenv())

ROOT_DIR = Path(__file__).resolve().parents[3]
SQLITE_DIR = ROOT_DIR / "infra" / "sqlite"
DB_NAME = "pararag_profiles.sqlite" if os.getenv("FOR_LOCOMO") == "true" else "user_profiles.sqlite"
DEFAULT_DB_PATH = SQLITE_DIR / DB_NAME


class SqliteAdapter(ProfileStore):
    def __init__(self, db_path: Path | None = None):
        db_path = db_path if db_path is not None else DEFAULT_DB_PATH
        super().__init__(db_path)


    async def init_store(self) -> None:
        """Initializes the whole profile store"""
        # Create parent folders if needed
        self.db_path.parent.mkdir(exist_ok=True, parents=True)

        # Create the table
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS user_profiles (
                    namespace TEXT NOT NULL,
                    username TEXT NOT NULL,
                    profile TEXT,

                    PRIMARY KEY (namespace, username)
                );
                """
            )
            await db.commit()


    async def init_profiles(self, usernames: list[str], namespace: str) -> None:
        """Initializes empty profiles for given users if absent"""
        async with aiosqlite.connect(self.db_path) as db:
            for username in usernames:
                await db.execute(
                    """
                    INSERT INTO user_profiles (namespace, username, profile)
                    VALUES (?, ?, ?)
                    ON CONFLICT(namespace, username) DO UPDATE SET
                        username = user_profiles.username,
                        profile = user_profiles.profile
                    """,
                    (namespace, username, None),
                )
            await db.commit()

        
    async def update_profile(self, new_profile: str, user: str, namespace: str) -> None:
        """Updates a user profile within a namespace"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                INSERT INTO user_profiles (namespace, username, profile)
                VALUES (?, ?, ?)
                ON CONFLICT(namespace, username) DO UPDATE SET
                    profile = excluded.profile
                """,
                (namespace, user, new_profile)
            )
            await db.commit()


    async def get_profiles(self, namespace: str) -> list[Profile]:
        """Returns all profiles from the namespace"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                """
                SELECT username, profile
                FROM user_profiles
                WHERE namespace = ?
                """,
                (namespace,)
            )
            rows = await cursor.fetchall()

            profiles = []
            for row in rows:
                profiles.append(
                    Profile(
                        name=row[0],
                        profile=row[1] if row[1] is not None else "" # Empty profiles become ""
                    )
                )
            return profiles
    
    async def delete_profiles(self, namespace: str) -> None:
        """Deletes all profiles from the current namespace"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                DELETE FROM user_profiles
                WHERE namespace = ?
                """,
                (namespace,)
            )
            await db.commit()
