from pydantic import BaseModel
from datetime import datetime
from textwrap import dedent


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
