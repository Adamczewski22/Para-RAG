from pararag.orchestration.shared.types import MemoryVersion
from pararag.orchestration.shared.base import MemoryOrchestrator
from pararag.orchestration.simple_decomposition.memory_orchestrator import SimpleDecompositionMemory
from pararag.orchestration.deduplication.memory_orchestrator import DeduplicationMemory
from pararag.orchestration.profiles.memory_orchestrator import ProfilesMemory
from pararag.memory.services.memory_retrieval_service import MemoryRetrievalService
from pararag.memory.services.memory_update_service import MemoryUpdateService
from pararag.memory.services.profile_service import ProfileService
from pararag.shared.logger import JsonLogger


def create_memory_orchestrator(
        version: MemoryVersion, 
        update_service: MemoryUpdateService, 
        retrieval_service: MemoryRetrievalService,
        profile_service: ProfileService,
        json_logger: JsonLogger | None = None,
        users: list[str] = [],
        query_decomposition: bool = True,
        parallel_mode: bool = True,
    ) -> MemoryOrchestrator:

    match version:
        case MemoryVersion.SIMPLE_DECOMPOSITION:
            return SimpleDecompositionMemory(
                update_service=update_service,
                retrieval_service=retrieval_service,
                profile_service=profile_service,
                json_logger=json_logger,
                users=users,
                query_decomposition=query_decomposition,
                parallel_mode=parallel_mode,
            )

        case MemoryVersion.DEDUPLICATION:
            return DeduplicationMemory(
                update_service=update_service,
                retrieval_service=retrieval_service,
                profile_service=profile_service,
                json_logger=json_logger,
                users=users,
                query_decomposition=query_decomposition,
                parallel_mode=parallel_mode,
            )
        
        case MemoryVersion.PROFILES:
            return ProfilesMemory(
                update_service=update_service,
                retrieval_service=retrieval_service,
                profile_service=profile_service,
                json_logger=json_logger,
                users=users,
                query_decomposition=query_decomposition,
                parallel_mode=parallel_mode,
            )

        case _:
            raise ValueError(f"Invalid memory orchestrator version: {version}")
