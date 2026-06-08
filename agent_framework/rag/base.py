from __future__ import annotations

from abc import ABC, abstractmethod


class RAGEngine(ABC):
    @abstractmethod
    def context_for(self, query: str) -> str:
        raise NotImplementedError


class NullRAGEngine(RAGEngine):
    def context_for(self, query: str) -> str:
        return ""
