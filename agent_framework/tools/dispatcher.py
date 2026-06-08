from __future__ import annotations

from agent_framework.core.events import EventSink
from agent_framework.core.types import ToolCall, ToolResult
from agent_framework.tools.registry import ToolRegistry


class ToolDispatcher:
    def __init__(self, registry: ToolRegistry, events: EventSink) -> None:
        self._registry = registry
        self._events = events

    def execute(self, call: ToolCall) -> ToolResult:
        self._events.emit("tool_call.started", call_id=call.call_id, name=call.name)
        tool = self._registry.get(call.name)
        if tool is None:
            result = ToolResult(
                call_id=call.call_id,
                name=call.name,
                content=f"Tool not found: {call.name}",
                ok=False,
            )
            self._events.emit(
                "tool_call.completed",
                call_id=call.call_id,
                name=call.name,
                ok=False,
            )
            return result

        try:
            result = tool.call(call)
        except Exception as exc:
            result = ToolResult(
                call_id=call.call_id,
                name=call.name,
                content=f"Tool error: {exc}",
                ok=False,
            )

        self._events.emit(
            "tool_call.completed",
            call_id=call.call_id,
            name=call.name,
            ok=result.ok,
        )
        return result
