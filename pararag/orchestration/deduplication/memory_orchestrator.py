from typing_extensions import override
from datetime import datetime

from pararag.shared.models import UserMessage
from pararag.orchestration.shared.base import BaseMemoryOrchestrator
from pararag.orchestration.simple_decomposition.retrieval import graph as retrieval_graph_module
from pararag.orchestration.shared.types import MemoryContext
from .update import graph as update_graph_module


class DeduplicationMemory(BaseMemoryOrchestrator):
    """Memory implementation with deduplicatin of memories"""
    """Extends simple decomposition memory with deduplication of similar memories"""

    update_graph = update_graph_module
    retrieval_graph = retrieval_graph_module

    @override
    async def add_user_msg(self, user_msg: UserMessage, timestamp: datetime, msg_id: str | None = None) -> None:
        """Extracts relevant facts from user message, and stores them in memory"""
        # Initialize the graph
        graph = self.update_graph.get_graph()
        graph_state = self.update_graph.init_graph_state(
            user_msg=user_msg,
            conversation_history=self.conversation_history,
            timestamp=timestamp,
            msg_id=msg_id,
        )

        # Deduplication memory requires both update and retrieval service for the update pipeline
        context = MemoryContext(
            retrieval_service=self.retrieval_service,
            update_service=self.update_service,
            json_logger=self.json_logger,
        )

        # Invoke the graph pipeline
        await graph.ainvoke(
            input=graph_state,
            context=context,
        )
        # Add user message conversation history (do not mistake wth main persistent memory)
        self.conversation_history.append(user_msg)
        self.conversation_history = self.conversation_history[-self.CONVERSATION_WINDOW:]
