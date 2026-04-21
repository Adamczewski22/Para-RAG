from pydantic import BaseModel
from .types import Vector
import datetime


class MemoryEntry:
    content: str
    embedding: Vector
    date: datetime
