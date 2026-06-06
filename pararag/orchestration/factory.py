from pararag.orchestration.shared.types import MemoryVersion
from pararag.orchestration.shared.base import MemoryOrchestrator
from pararag.orchestration.simple_decomposition.memory_orchestrator import SimpleDecompositionMemory
from pararag.orchestration.deduplication.memory_orchestrator import DeduplicationMemory
from pararag.memory.services.memory_retrieval_service import MemoryRetrievalService
from pararag.memory.services.memory_update_service import MemoryUpdateService
from pararag.shared.logger import JsonLogger


def create_memory_orchestrator(
        version: MemoryVersion, 
        update_service: MemoryUpdateService, 
        retrieval_service: MemoryRetrievalService,
        json_logger: JsonLogger | None = None,
    ) -> MemoryOrchestrator:

    match version:
        case MemoryVersion.SIMPLE_DECOMPOSITION:
            return SimpleDecompositionMemory(
                update_service=update_service,
                retrieval_service=retrieval_service,
                json_logger=json_logger,
            )

        case MemoryVersion.DEDUPLICATION:
            return DeduplicationMemory(
                update_service=update_service,
                retrieval_service=retrieval_service,
                json_logger=json_logger,
            )

        case _:
            raise ValueError(f"Invalid memory orchestrator version: {version}")
