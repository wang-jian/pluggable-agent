from __future__ import annotations

from abc import ABC, abstractmethod


class MemoryStore(ABC):
    def start_turn(self, user_input: str) -> None:
        return None

    @abstractmethod
    def context_for(self, query: str) -> str:
        raise NotImplementedError

    def finish_turn(self, user_input: str, assistant_output: str) -> None:
        return None

    @abstractmethod
    def remember(self, key: str, value: str) -> None:
        raise NotImplementedError


class NullMemoryStore(MemoryStore):
    def context_for(self, query: str) -> str:
        return ""

    def remember(self, key: str, value: str) -> None:
        return None
