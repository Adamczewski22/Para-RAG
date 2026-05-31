from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
import asyncio

from pararag import ParaRAGMemory, MemoryEntry, MemoryVersion, get_console


MEMORY_VERSION = MemoryVersion.DEDUPLICATION


PROMPT = """You are a virtual personal assistant. 
    Rules:
        - Be helpful and friendly.
        - Use only the provided MEMORIES as a source of long-term memory about the user and your past conversations.
        - The MEMORIES are a very important source of information. Use them to ensure personalization.
        - Apart from that you may use your general knowledge.
        - Please answer in 1-2 sentences if possible.
    
    MEMORIES:
    {memories}
    END OF MEMORIES
"""

def memories_to_str(memories: list[MemoryEntry]) -> str:
    return "\n".join([str(memory) for memory in memories])

async def main():
    llm = ChatOpenAI(model="gpt-5.2")
    memory = ParaRAGMemory(memory_version=MEMORY_VERSION)

    # With ParaRAG being well-suited for long-term memory, for very short-term memory it is good to use a history of recent messages.
    conversation_history = []
    conversation_window = 5

    # A conversational loop between a user and a simple chatbot assistant
    user_msg = input("User: ")
    while user_msg.strip().lower() != "exit":
        # Add user msg to conversation history
        conversation_history.append(HumanMessage(user_msg))
        conversation_history = conversation_history[-conversation_window:]

        # Fetch memories relevant to the current user message from ParaRAG memory
        memories = await memory.retrieve_memories(user_msg)
        memories_str = memories_to_str(memories)

        # Construct the system message
        system_msg = SystemMessage(PROMPT.format(memories=memories_str))

        # Call the assistant with retrieved memories
        messages = [system_msg] + conversation_history
        response = await llm.ainvoke(messages)
        assistant_msg = response.content
        get_console().print_assistant_msg(assistant_msg)

        # Update ParaRAG memory
        await memory.add_conversation_turn(
            user_msg=user_msg,
            assistant_msg=assistant_msg,
        )

        # Add assistant msg to conversation history
        conversation_history.append(response)

        get_console().print_prompt_user()
        user_msg = input()


if __name__ == "__main__":
    asyncio.run(main())