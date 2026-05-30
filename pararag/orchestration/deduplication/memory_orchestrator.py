from dotenv import load_dotenv, find_dotenv
from datetime import datetime

from pararag.orchestration.shared.base import BaseMemoryOrchestrator
from .retrieval import graph as retrieval_graph_module
from .update import graph as update_graph_module


class DeduplicationMemory(BaseMemoryOrchestrator):
    """Memory implementation with deduplicatin of memories"""
    """Extends simple decomposition memory with deduplication of similar memories"""

    update_graph = update_graph_module
    retrieval_graph = retrieval_graph_module
