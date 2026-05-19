from pydantic import BaseModel, StringConstraints, Field
from datetime import datetime
from typing import Annotated

from pararag import MemoryVersion, MemoryEntry, Collection
from pararag_server.types import MessageType

SPEAKER_MAX_LEN = 50
MEMORY_ID_MAX_LEN = 50
CONTENT_MAX_LEN = 1000


class MemorySelector(BaseModel):
    memory_version: Annotated[
        MemoryVersion,
        Field(description="", examples=[""]),
    ] | None = None

    memory_id: Annotated[
        str,
        StringConstraints(max_length=MEMORY_ID_MAX_LEN),
        Field(description="", examples=[""]),
    ] | None = None


class MessagesRequest(MemorySelector):
    message_type: Annotated[
        MessageType,
        Field(description="", examples=[""]),
    ]

    speaker: Annotated[
        str, 
        StringConstraints(max_length=SPEAKER_MAX_LEN), 
        Field(description="", examples=[""]),
    ] | None = None

    content: Annotated[
        str,
        StringConstraints(max_length=CONTENT_MAX_LEN),
        Field(description="", examples=[""]),
    ]

    timestamp: Annotated[
        datetime,
        Field(description="", examples=[""]),
    ] | None = None


class RetrieveRequest(MemorySelector):
    user_msg: Annotated[
        str,
        StringConstraints(max_length=CONTENT_MAX_LEN),
        Field(description="", examples=[""]),
    ]

class RetrieveResponse(BaseModel):
    memories: list[MemoryEntry] = Field(description="", examples=[""])


class ClearCollectionRequest(MemorySelector):
    collection: Collection = Field(description="", examples=[""])
