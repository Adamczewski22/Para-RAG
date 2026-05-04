from langchain_core.messages import HumanMessage, AIMessage

from pararag.orchestration import MemoryOrchestrator, MemoryVersion, create_memory_orchestrator
from pararag.shared.models import MemoryEntry

DEFAULT_MEMORY_VERSION = MemoryVersion.SIMPLE_DECOMPOSITION


class ParaRAGMemory:
    """The ParaRAG framework facade implementing conversational memory"""
    def __init__(self, memory_version: MemoryVersion = DEFAULT_MEMORY_VERSION):
        self.orchestrator: MemoryOrchestrator = create_memory_orchestrator(
            version=memory_version
        )

    async def retrieve_memories(self, user_msg: str) -> list[MemoryEntry]:
        """Retrieves relevant memories for answering a user message as an aid to a chatbot assistant"""
        user_msg_obj = HumanMessage(user_msg)
        return await self.orchestrator.retrieve(user_msg_obj)

    async def add_conversation_turn(self, user_msg: str, assistant_msg: str) -> None:
        """Updates memory based on one conversation turn: user messages followed by an assistant message"""
        await self.add_user_msg(user_msg)
        await self.add_assistant_msg(assistant_msg)
    
    async def add_user_msg(self, user_msg: str) -> None:
        """Updates memory based on user's message"""
        user_msg_obj = HumanMessage(user_msg)
        await self.orchestrator.add_user_msg(user_msg_obj)
    
    async def add_assistant_msg(self, assistant_msg: str) -> None:
        """Updates memory based on assistant's message"""
        assistant_msg_obj = AIMessage(assistant_msg)
        await self.orchestrator.add_assistant_msg(assistant_msg_obj)
