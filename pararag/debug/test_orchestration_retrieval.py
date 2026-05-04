from langchain_core.messages import HumanMessage
import asyncio

from pararag.orchestration.simple_decomposition.memory_orchestrator import SimpleDecompositionMemory

async def main():
    orchestrator = SimpleDecompositionMemory()
    memories = await orchestrator.retrieve(HumanMessage("What did I consider romantic in Amsterdam and what do I like cats?"))
    print(memories)

if __name__ == "__main__":
    asyncio.run(main())
