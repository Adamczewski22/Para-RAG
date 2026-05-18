from datetime import datetime
from pararag.shared.models import MemoryEntry

def memory_to_payload(memory: MemoryEntry, namespace: str) -> dict[str, object]:
    return {
        "id": memory.id,
        "content": memory.content,
        "date": memory.date.isoformat(),
        "namespace": namespace,
    }

def payload_to_memory(payload: dict) -> MemoryEntry:
    return MemoryEntry(
        id=payload["id"],
        content=payload["content"],
        date=datetime.fromisoformat(payload["date"]),
    )