from langchain_core.messages import HumanMessage, AIMessage
import asyncio

from pararag.orchestration.simple_decomposition.memory_orchestrator import SimpleDecompositionMemory


async def main():
    memory_system = SimpleDecompositionMemory()
    while True:
        user_msg = HumanMessage(input("User: "))
        memories = await memory_system.retrieve(user_msg)
        print(memories)
        for memory in memories:
            print(memory.model_dump_json(indent=2))

        await memory_system.add_user_msg(user_msg)

        ai_msg = AIMessage(input("Assistant: "))
        await memory_system.add_assistant_msg(ai_msg)

asyncio.run(main())
