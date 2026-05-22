from datetime import datetime
from pydantic import BaseModel
from textwrap import dedent
from enum import StrEnum
import httpx


SERVER_TIMEOUT = 15
SERVER_URL = "http://20.123.194.67:8000"


class MemoryVersion(StrEnum):
    SIMPLE_DECOMPOSITION = "simple_decomposition"


class MemoryEntry(BaseModel):
    id: str
    content: str
    date: datetime

    def __str__(self) -> str:
        return dedent(f"""
            MemoryEntry:
                date: {self.date:%Y-%m-%d %H:%M}
                content: {self.content}
        """).strip()

    def __repr__(self) -> str:
        return self.__str__()


class ParaRAGClient:
    def __init__(self, memory_id: str, memory_version: MemoryVersion = MemoryVersion.SIMPLE_DECOMPOSITION):
        self.memory_id = memory_id
        self.memory_version = memory_version


    async def retrieve_memories(self, user_msg: str) -> list[MemoryEntry]:
        """Retrieves relevant memories for answering a user message as an aid to a chatbot assistant"""
        async with httpx.AsyncClient(timeout=SERVER_TIMEOUT) as client:
            response = await client.post(
                f"{SERVER_URL}/retrieve",
                json={
                    "memory_version": self.memory_version,
                    "memory_id": self.memory_id,
                    "user_msg": user_msg,
                }
            )
        response.raise_for_status()
        memories = response.json()["memories"]
        return [MemoryEntry.model_validate(memory) for memory in memories]


    async def add_conversation_turn(
            self, user_msg: str, 
            assistant_msg: str, 
            timestamp: datetime | None = None
    ) -> None:
        """Updates memory based on one conversation turn: user messages followed by an assistant message"""
        await self.add_user_msg(user_msg=user_msg, timestamp=timestamp)
        await self.add_assistant_msg(assistant_msg=assistant_msg, timestamp=timestamp)


    async def add_user_msg(
            self, 
            user_msg: str, 
            speaker: str | None = None, 
            timestamp: datetime | None = None
    ) -> None:
        """Updates memory based on user's message"""
        async with httpx.AsyncClient(timeout=SERVER_TIMEOUT) as client:
            response = await client.post(
                f"{SERVER_URL}/messages",
                json={
                    "memory_version": self.memory_version,
                    "memory_id": self.memory_id,
                    "message_type": "user",
                    "speaker": speaker,
                    "content": user_msg,
                    "timestamp": timestamp.isoformat() if timestamp is not None else None,
                }
            )
        response.raise_for_status()


    async def add_assistant_msg(
            self, 
            assistant_msg: str, 
            timestamp: datetime | None = None
    ) -> None:
        """Updates memory based on assistant's message"""
        async with httpx.AsyncClient(timeout=SERVER_TIMEOUT) as client:
            response = await client.post(
                f"{SERVER_URL}/messages",
                json={
                    "memory_version": self.memory_version,
                    "memory_id": self.memory_id,
                    "message_type": "assistant",
                    "speaker": None,
                    "content": assistant_msg,
                    "timestamp": timestamp.isoformat() if timestamp is not None else None,
                }
            )
        response.raise_for_status()
