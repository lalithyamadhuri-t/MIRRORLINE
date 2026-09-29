from datetime import datetime
from typing import Any
from uuid import uuid4

class MemoryService:
    """
    Local deterministic memory adapter.

    The application talks to memory through retain/recall/reflect so that
    Hindsight can be connected without rewriting the learning engine.
    For the first runnable prototype, memories are persisted in process memory.
    """

    def __init__(self):
        self.memories: list[dict[str, Any]] = []

    def retain(self, experience: dict[str, Any]) -> dict[str, Any]:
        record = dict(experience)
        record.setdefault("memory_id", str(uuid4()))
        record.setdefault("retained_at", datetime.utcnow().isoformat())
        self.memories.append(record)
        return record

    def recall(self, query: str, limit: int = 20) -> list[dict[str, Any]]:
        q = query.lower()
        tokens = {t for t in q.replace(",", " ").split() if len(t) > 2}
        scored = []
        for memory in self.memories:
            text = " ".join([
                str(memory.get("action", "")),
                str(memory.get("actual_outcome", "")),
                " ".join(memory.get("conditions", [])),
                " ".join(memory.get("entities", [])),
                str(memory.get("lesson", "")),
            ]).lower()
            score = sum(1 for token in tokens if token in text)
            if score:
                scored.append((score, memory))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [m for _, m in scored[:limit]]

    def reflect(self, memories: list[dict[str, Any]]) -> dict[str, Any]:
        successes = sum(1 for m in memories if m.get("status") == "success")
        failures = sum(1 for m in memories if m.get("status") == "failure")
        return {
            "memory_count": len(memories),
            "successes": successes,
            "failures": failures,
            "dominant_status": "success" if successes > failures else "failure" if failures > successes else "mixed",
        }

    def clear(self):
        self.memories.clear()
