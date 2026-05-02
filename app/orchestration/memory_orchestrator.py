from langchain_core.messages import BaseMessage, HumanMessage
from dotenv import load_dotenv, find_dotenv

from app.orchestration.graph import get_graph, init_graph_state
from app.shared.models import MemoryEntry

load_dotenv(find_dotenv())


class MemoryOrchestrator:
    def __init__(self):
        self.conversation_history = []
    
    async def update(self, msg: BaseMessage) -> None:
        conversation_window = 6 # Does not restrict the overall memory. This concerns internals of graph logic.
        self.conversation_history.append(msg)
        self.conversation_history = self.conversation_history[-conversation_window]
        # TODO: update the store

    async def retrieve(self, user_msg: HumanMessage) -> list[MemoryEntry]:
        graph = get_graph()
        graph_state = init_graph_state(user_msg, self.conversation_history)
        
        result = await graph.ainvoke(input=graph_state)
        return result["memories"]