from __future__ import annotations

from abc import ABC, abstractmethod

from agent_framework.tools.base import Tool


class MCPClient(ABC):
    @abstractmethod
    def tools_for(self, query: str) -> list[Tool]:
        raise NotImplementedError


class NullMCPClient(MCPClient):
    def tools_for(self, query: str) -> list[Tool]:
        return []
