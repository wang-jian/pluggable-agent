from __future__ import annotations

from dataclasses import dataclass, field

from agent_framework.tools.base import Tool


@dataclass(frozen=True)
class Agent:
    name: str
    instructions: str
    tools: list[Tool] = field(default_factory=list)
