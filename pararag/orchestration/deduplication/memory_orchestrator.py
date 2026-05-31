from pararag.orchestration.shared.base import BaseMemoryOrchestrator
from pararag.orchestration.simple_decomposition.retrieval import graph as retrieval_graph_module
from .update import graph as update_graph_module


class DeduplicationMemory(BaseMemoryOrchestrator):
    """Memory implementation with deduplicatin of memories"""
    """Extends simple decomposition memory with deduplication of similar memories"""

    update_graph = update_graph_module
    retrieval_graph = retrieval_graph_module
