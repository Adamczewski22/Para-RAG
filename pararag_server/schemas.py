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
        Field(
            description="Memory implementation to use.",
            examples=["simple_decomposition"],
        ),
    ] | None = None

    memory_id: Annotated[
        str,
        StringConstraints(max_length=MEMORY_ID_MAX_LEN),
        Field(
            description="Identifier for the memory namespace.",
            examples=["demo-user"],
        ),
    ] | None = None


class MessagesRequest(MemorySelector):
    message_type: Annotated[
        MessageType,
        Field(
            description="Role of the message being added.",
            examples=["user"],
        ),
    ]

    speaker: Annotated[
        str, 
        StringConstraints(max_length=SPEAKER_MAX_LEN), 
        Field(
            description="Optional display name for the user speaker.",
            examples=["Alice"],
        ),
    ] | None = None

    content: Annotated[
        str,
        StringConstraints(max_length=CONTENT_MAX_LEN),
        Field(
            description="Message text to add to memory.",
            examples=["The canals of Amsterdam are very romantic"],
        ),
    ]

    timestamp: Annotated[
        datetime,
        Field(
            description="Optional time when the message was sent.",
            examples=["2026-05-19T14:30:00Z"],
        ),
    ] | None = None


class RetrieveRequest(MemorySelector):
    user_msg: Annotated[
        str,
        StringConstraints(max_length=CONTENT_MAX_LEN),
        Field(
            description="User message to retrieve relevant memories for.",
            examples=["What do you remember about my work?"],
        ),
    ]

class RetrieveResponse(BaseModel):
    memories: list[MemoryEntry] = Field(
        description="Memories relevant to the retrieval query.",
        examples=[
            [
                {
                    "id": "17c4822c-2ba2-4437-91b6-50d039188f65",
                    "content": "User finds the canals of Amsterdam romantic",
                    "date": "2026-05-19T14:30:00Z",
                }
            ]
        ],
    )


class ClearCollectionRequest(MemorySelector):
    collection: Collection = Field(
        description="Memory collection to clear.",
        examples=["assertions"],
    )
