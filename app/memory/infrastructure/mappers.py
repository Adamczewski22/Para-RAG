from datetime import datetime
from app.shared.models import MemoryEntry

def memory_to_payload(memory: MemoryEntry) -> dict[str, object]:
    return {
        "content": memory.content,
        "date": memory.date.isoformat(),
    }

def payload_to_memory(payload: dict) -> MemoryEntry:
    return MemoryEntry(
        content=payload["content"],
        date=datetime.fromisoformat(payload["date"]),
    )