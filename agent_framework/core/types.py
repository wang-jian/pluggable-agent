from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Literal
from uuid import uuid4


class FinishReason(str, Enum):
    FINAL = "final"
    MAX_TURNS = "max_turns"
    NO_TOOL_CALLS = "no_tool_calls"
    TOOL_ERROR = "tool_error"


@dataclass(frozen=True)
class ToolCall:
    name: str
    arguments: dict[str, Any] = field(default_factory=dict)
    call_id: str = field(default_factory=lambda: str(uuid4()))


@dataclass(frozen=True)
class ToolResult:
    call_id: str
    name: str
    content: str
    ok: bool = True
    data: Any | None = None


@dataclass(frozen=True)
class ModelOutput:
    content: str = ""
    tool_calls: list[ToolCall] = field(default_factory=list)
    final: bool = False


@dataclass(frozen=True)
class Message:
    role: Literal["system", "user", "assistant", "tool"]
    content: str
    name: str | None = None
    tool_call_id: str | None = None


@dataclass
class LoopResult:
    answer: str
    finish_reason: FinishReason
    messages: list[Message]
    turns: int
