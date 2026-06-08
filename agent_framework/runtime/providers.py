from __future__ import annotations

from collections.abc import Callable
from typing import Any, TypeVar

from agent_framework.memory.base import NullMemoryStore
from agent_framework.mcp.base import NullMCPClient
from agent_framework.rag.base import NullRAGEngine
from agent_framework.runtime.config import CapabilityConfig, RuntimeConfig
from agent_framework.runtime.runtime import AgentRuntime
from agent_framework.skills.base import NullSkillLoader
from agent_framework.tools.providers import NullToolProvider

T = TypeVar("T")
ProviderFactory = Callable[[dict[str, Any]], Any]


class ProviderRegistry:
    def __init__(self) -> None:
        self._providers: dict[tuple[str, str], ProviderFactory] = {}
        self.register("memory", "none", lambda options: NullMemoryStore())
        self.register("rag", "none", lambda options: NullRAGEngine())
        self.register("mcp", "none", lambda options: NullMCPClient())
        self.register("skills", "none", lambda options: NullSkillLoader())
        self.register("tools", "none", lambda options: NullToolProvider())

    def register(self, capability: str, provider: str, factory: ProviderFactory) -> None:
        key = (capability, provider)
        if key in self._providers:
            raise ValueError(f"duplicate provider registered: {capability}:{provider}")
        self._providers[key] = factory

    def create(self, capability: str, config: CapabilityConfig) -> Any:
        factory = self._providers.get((capability, config.provider))
        if factory is None:
            raise ValueError(f"provider not registered: {capability}:{config.provider}")
        return factory(config.options)


class RuntimeBuilder:
    def __init__(self, registry: ProviderRegistry) -> None:
        self._registry = registry

    def build(self, config: RuntimeConfig) -> AgentRuntime:
        return AgentRuntime(
            model=self._registry.create("model", config.model),
            memory=self._registry.create("memory", config.memory),
            rag=self._registry.create("rag", config.rag),
            mcp=self._registry.create("mcp", config.mcp),
            skills=self._registry.create("skills", config.skills),
            tools=self._registry.create("tools", config.tools),
        )
