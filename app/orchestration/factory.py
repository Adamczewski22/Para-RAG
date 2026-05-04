from app.orchestration.shared.types import MemoryOrchestratorVersion
from app.orchestration.simple_decomposition.memory_orchestrator import SimpleDecompositionMemory

def create_memory_orchestrator(version: MemoryOrchestratorVersion):
    match version:
        case MemoryOrchestratorVersion.SIMPLE_DECOMPOSITION:
            return SimpleDecompositionMemory()

        case _:
            raise ValueError("Invalid memory orchestrator version")
