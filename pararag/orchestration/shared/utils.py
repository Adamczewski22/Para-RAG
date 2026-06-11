from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from pararag.shared.models import Message, MemoryEntry


def messages_to_string(messages: list[Message]) -> str:
    """Converts list of message objects into a string representation"""
    messages_str = [str(msg) for msg in messages]
    return "\n".join(messages_str)


def assertions_to_string(assertions: list[str]) -> str:
    """Converts list of assertions into a string representation"""
    results = ""
    for assertion in assertions:
        results += f"- {assertion}\n"
    return results


def langchain_messages_to_string(messages: list[BaseMessage]) -> str:
    """Converts list of langchain message objects into a string representation"""
    lines = []
    for m in messages:
        if isinstance(m, HumanMessage):
            role = "User"
        elif isinstance(m, AIMessage):
            role = "Assistant"
        elif isinstance(m, SystemMessage):
            role = "System"
        else:
            role = "Unknown"

        lines.append(f"{role}: {m.content}")

    return "\n".join(lines)


def memories_to_str(memories: list[MemoryEntry]) -> str:
    return "\n".join([str(memory) for memory in memories])
    