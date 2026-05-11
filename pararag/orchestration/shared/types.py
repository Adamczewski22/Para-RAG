from typing import TypedDict
from enum import StrEnum

from pararag.memory.services.memory_retrieval_service import MemoryRetrievalService
from pararag.memory.services.memory_update_service import MemoryUpdateService

class MemoryVersion(StrEnum):
    SIMPLE_DECOMPOSITION = "simple_decomposition"

class RetrievalContext(TypedDict):
    retrieval_service: MemoryRetrievalService

class UpdateContext(TypedDict):
    update_service: MemoryUpdateService
