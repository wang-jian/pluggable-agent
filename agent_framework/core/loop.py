from __future__ import annotations

from agent_framework.core.agent import Agent
from agent_framework.core.events import EventSink, InMemoryEventSink
from agent_framework.core.model import ModelAdapter
from agent_framework.core.types import FinishReason, LoopResult, Message, ToolResult
from agent_framework.runtime.runtime import AgentRuntime
from agent_framework.tools.dispatcher import ToolDispatcher
from agent_framework.tools.registry import ToolRegistry


class AgentLoop:
    def __init__(
        self,
        model: ModelAdapter | None = None,
        *,
        runtime: AgentRuntime | None = None,
        max_turns: int = 8,
        events: EventSink | None = None,
        stop_on_tool_error: bool = False,
    ) -> None:
        if max_turns < 1:
            raise ValueError("max_turns must be >= 1")
        if model is None and runtime is None:
            raise ValueError("model or runtime is required")
        if model is not None and runtime is not None:
            raise ValueError("pass either model or runtime, not both")
        self._runtime = runtime or AgentRuntime(model=model)
        self._max_turns = max_turns
        self.events = events or InMemoryEventSink()
        self._stop_on_tool_error = stop_on_tool_error

    def run(self, agent: Agent, user_input: str) -> LoopResult:
        messages = self._runtime.build_messages(agent, user_input)
        registry = ToolRegistry(self._runtime.build_tools(agent, user_input))
        dispatcher = ToolDispatcher(registry, self.events)

        self.events.emit("turn.started", agent=agent.name)

        last_assistant_text = ""
        for turn_index in range(self._max_turns):
            self.events.emit("model_call.started", turn=turn_index + 1)
            output = self._runtime.model.generate(agent, messages)
            last_assistant_text = output.content
            messages.append(Message(role="assistant", content=output.content))
            self.events.emit(
                "model_call.completed",
                turn=turn_index + 1,
                final=output.final,
                tool_calls=len(output.tool_calls),
            )

            if output.final:
                self.events.emit("turn.completed", reason=FinishReason.FINAL.value)
                return LoopResult(
                    answer=output.content,
                    finish_reason=FinishReason.FINAL,
                    messages=messages,
                    turns=turn_index + 1,
                )

            if not output.tool_calls:
                self.events.emit("turn.completed", reason=FinishReason.NO_TOOL_CALLS.value)
                return LoopResult(
                    answer=output.content,
                    finish_reason=FinishReason.NO_TOOL_CALLS,
                    messages=messages,
                    turns=turn_index + 1,
                )

            tool_results: list[ToolResult] = []
            for call in output.tool_calls:
                result = dispatcher.execute(call)
                tool_results.append(result)
                messages.append(
                    Message(
                        role="tool",
                        name=result.name,
                        tool_call_id=result.call_id,
                        content=result.content,
                    )
                )

            if self._stop_on_tool_error and any(not result.ok for result in tool_results):
                self.events.emit("turn.completed", reason=FinishReason.TOOL_ERROR.value)
                return LoopResult(
                    answer=self._format_tool_errors(tool_results),
                    finish_reason=FinishReason.TOOL_ERROR,
                    messages=messages,
                    turns=turn_index + 1,
                )

        self.events.emit("turn.completed", reason=FinishReason.MAX_TURNS.value)
        return LoopResult(
            answer=last_assistant_text,
            finish_reason=FinishReason.MAX_TURNS,
            messages=messages,
            turns=self._max_turns,
        )

    @staticmethod
    def _format_tool_errors(results: list[ToolResult]) -> str:
        errors = [result.content for result in results if not result.ok]
        return "\n".join(errors)
