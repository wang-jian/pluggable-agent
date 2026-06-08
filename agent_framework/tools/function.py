from __future__ import annotations

from collections.abc import Callable
from typing import Any

from agent_framework.core.types import ToolCall, ToolResult
from agent_framework.tools.base import Tool, ToolSpec


class FunctionTool(Tool):
    def __init__(
        self,
        name: str,
        description: str,
        input_schema: dict[str, Any],
        fn: Callable[..., Any],
    ) -> None:
        self._spec = ToolSpec(
            name=name,
            description=description,
            input_schema=input_schema,
        )
        self._fn = fn

    def spec(self) -> ToolSpec:
        return self._spec

    def call(self, call: ToolCall) -> ToolResult:
        value = self._fn(**call.arguments)
        return ToolResult(
            call_id=call.call_id,
            name=call.name,
            content=str(value),
            ok=True,
            data=value,
        )
