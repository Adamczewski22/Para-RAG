from typing_extensions import override
from datetime import datetime
import time

from pararag.shared.models import UserMessage
from pararag.orchestration.shared.base import BaseMemoryOrchestrator
from pararag.orchestration.shared.types import ProfileUpdateContext
from pararag.orchestration.simple_decomposition.retrieval import graph as retrieval_graph_module
from pararag.orchestration.profiles.update.nodes import update_profiles_from_assertions
from .update import graph as update_graph_module


class ProfilesMemory(BaseMemoryOrchestrator):
    """Memory implementation with additional user profiles
    Extends deduplication memory with user profiles for key, stable user information"""

    update_graph = update_graph_module
    retrieval_graph = retrieval_graph_module
    PROFILE_UPDATE_INTERVAL = 6

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._pending_profile_assertions: list[str] = []
        self._messages_since_profile_update = 0

    @override
    async def add_user_msg(
        self, 
        user_msg: UserMessage, 
        timestamp: datetime, 
        msg_id: str | None = None, 
        assertions: list[str] | None = None,
        deduplicated_assertions: list[str] | None = None,
    ) -> None:
        """Extracts relevant facts from user message, and stores them in memory"""
        update_start = time.perf_counter()

        # Initialize the graph
        graph = self.update_graph.get_graph()
        graph_state = self.update_graph.init_graph_state(
            user_msg=user_msg,
            conversation_history=self.conversation_history,
            timestamp=timestamp,
            msg_id=msg_id,
            parallel_mode=self.parallel_mode,
            assertions=assertions,
            deduplicated_assertions=deduplicated_assertions,
            users=self.users,
        )

        # Setup runtime context
        context = ProfileUpdateContext(
            retrieval_service=self.retrieval_service,
            update_service=self.update_service,
            json_logger=self.json_logger,
            profile_service=self.profile_service,
        )

        # Invoke the graph pipeline
        result = await graph.ainvoke(
            input=graph_state,
            context=context,
        )

        deduplicated = result.get("deduplicated_assertions")
        if deduplicated is None:
            deduplicated = deduplicated_assertions or []

        self._pending_profile_assertions.extend(deduplicated)
        self._messages_since_profile_update += 1

        if self._messages_since_profile_update >= self.PROFILE_UPDATE_INTERVAL:
            await self.force_profile_update(msg_id=msg_id)

        # Add user message conversation history (do not mistake wth main persistent memory)
        self.conversation_history.append(user_msg)
        self.conversation_history = self.conversation_history[-self.CONVERSATION_WINDOW:]

        # Log update latency
        if msg_id is not None and self.json_logger is not None:
            self.json_logger.log_update_latency(
                msg_id=msg_id,
                latency=time.perf_counter() - update_start,
            )

    async def force_profile_update(self, msg_id: str | None = None) -> None:
        """Updates profiles from all deduplicated assertions collected since the last profile update."""
        if len(self._pending_profile_assertions) == 0:
            self._messages_since_profile_update = 0
            return

        await update_profiles_from_assertions(
            assertions=self._pending_profile_assertions,
            users=self.users,
            profile_service=self.profile_service,
            json_logger=self.json_logger,
            msg_id=msg_id,
        )
        self._pending_profile_assertions = []
        self._messages_since_profile_update = 0
