from __future__ import annotations

from agent_framework.memory.base import MemoryStore


class LocalMemoryStore(MemoryStore):
    def __init__(self, entries: dict[str, str] | None = None) -> None:
        self._entries = dict(entries or {})

    def context_for(self, query: str) -> str:
        if not self._entries:
            return ""
        return "\n".join(f"- {key}: {value}" for key, value in sorted(self._entries.items()))

    def remember(self, key: str, value: str) -> None:
        self._entries[key] = value
