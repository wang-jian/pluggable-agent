from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class CapabilityConfig:
    provider: str
    options: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RuntimeConfig:
    model: CapabilityConfig
    memory: CapabilityConfig = field(default_factory=lambda: CapabilityConfig("none"))
    rag: CapabilityConfig = field(default_factory=lambda: CapabilityConfig("none"))
    mcp: CapabilityConfig = field(default_factory=lambda: CapabilityConfig("none"))
    skills: CapabilityConfig = field(default_factory=lambda: CapabilityConfig("none"))
    tools: CapabilityConfig = field(default_factory=lambda: CapabilityConfig("none"))
