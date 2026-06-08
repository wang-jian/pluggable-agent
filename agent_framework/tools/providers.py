from __future__ import annotations

from abc import ABC, abstractmethod

from agent_framework.tools.base import Tool


class ToolProvider(ABC):
    @abstractmethod
    def tools_for(self, query: str) -> list[Tool]:
        raise NotImplementedError


class NullToolProvider(ToolProvider):
    def tools_for(self, query: str) -> list[Tool]:
        return []


class StaticToolProvider(ToolProvider):
    def __init__(self, tools: list[Tool]) -> None:
        self._tools = list(tools)

    def tools_for(self, query: str) -> list[Tool]:
        return list(self._tools)
