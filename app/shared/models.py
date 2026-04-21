from pydantic import BaseModel
from .types import Vector
from datetime import datetime


class MemoryEntry(BaseModel):
    content: str
    date: datetime
