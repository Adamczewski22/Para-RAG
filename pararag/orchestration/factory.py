from pararag.orchestration.shared.types import MemoryVersion
from pararag.orchestration.simple_decomposition.memory_orchestrator import SimpleDecompositionMemory

def create_memory_orchestrator(version: MemoryVersion):
    match version:
        case MemoryVersion.SIMPLE_DECOMPOSITION:
            return SimpleDecompositionMemory()

        case _:
            raise ValueError("Invalid memory orchestrator version")
