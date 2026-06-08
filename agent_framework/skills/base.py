from __future__ import annotations

from abc import ABC, abstractmethod

from agent_framework.tools.base import Tool


class SkillLoader(ABC):
    @abstractmethod
    def instructions_for(self, query: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def tools_for(self, query: str) -> list[Tool]:
        raise NotImplementedError


class NullSkillLoader(SkillLoader):
    def instructions_for(self, query: str) -> str:
        return ""

    def tools_for(self, query: str) -> list[Tool]:
        return []
