from __future__ import annotations

from abc import ABC, abstractmethod


class MemoryStore(ABC):
    @abstractmethod
    def context_for(self, query: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def remember(self, key: str, value: str) -> None:
        raise NotImplementedError


class NullMemoryStore(MemoryStore):
    def context_for(self, query: str) -> str:
        return ""

    def remember(self, key: str, value: str) -> None:
        return None
