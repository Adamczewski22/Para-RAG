from typing import TypedDict
from enum import StrEnum

from pararag.memory.services.memory_retrieval_service import MemoryRetrievalService
from pararag.memory.services.memory_update_service import MemoryUpdateService
from pararag.memory.services.profile_service import ProfileService
from pararag.shared.logger import JsonLogger

class MemoryVersion(StrEnum):
    SIMPLE_DECOMPOSITION = "simple_decomposition"
    DEDUPLICATION = "deduplication"
    PROFILES = "profiles"


class RetrievalContext(TypedDict):
    retrieval_service: MemoryRetrievalService

class UpdateContext(TypedDict):
    update_service: MemoryUpdateService
    json_logger: JsonLogger

class MemoryContext(RetrievalContext, UpdateContext):
    pass

class ProfileUpdateContext(MemoryContext):
    profile_service: ProfileService
