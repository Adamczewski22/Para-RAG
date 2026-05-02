from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage


def messages_to_string(messages: list[BaseMessage]) -> str:
    """Converts list of message objects into a string representation"""
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