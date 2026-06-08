from __future__ import annotations

from agent_framework import Agent, AgentLoop
from agent_framework.core.model import ModelAdapter
from agent_framework.core.types import FinishReason, Message, ModelOutput, ToolCall
from agent_framework.memory.local import LocalMemoryStore
from agent_framework.runtime import CapabilityConfig, ProviderRegistry, RuntimeBuilder, RuntimeConfig
from agent_framework.tools.function import FunctionTool
from agent_framework.tools.providers import StaticToolProvider


class FinalModel(ModelAdapter):
    def generate(self, agent: Agent, messages: list[Message]) -> ModelOutput:
        return ModelOutput(content="done", final=True)


class ToolThenFinalModel(ModelAdapter):
    def generate(self, agent: Agent, messages: list[Message]) -> ModelOutput:
        if not any(message.role == "tool" for message in messages):
            return ModelOutput(
                content="calling tool",
                tool_calls=[ToolCall(name="add", arguments={"a": 1, "b": 2})],
            )
        return ModelOutput(content="answer: 3", final=True)


class UnknownToolModel(ModelAdapter):
    def generate(self, agent: Agent, messages: list[Message]) -> ModelOutput:
        return ModelOutput(
            content="calling missing tool",
            tool_calls=[ToolCall(name="missing", arguments={})],
        )


class ContextEchoModel(ModelAdapter):
    def generate(self, agent: Agent, messages: list[Message]) -> ModelOutput:
        return ModelOutput(content=messages[0].content, final=True)


def test_final_answer_returns_immediately() -> None:
    agent = Agent(name="agent", instructions="test")
    result = AgentLoop(FinalModel()).run(agent, "hello")

    assert result.answer == "done"
    assert result.finish_reason == FinishReason.FINAL
    assert result.turns == 1


def test_tool_result_is_fed_back_to_model() -> None:
    tool = FunctionTool(
        name="add",
        description="Add numbers",
        input_schema={"type": "object"},
        fn=lambda a, b: a + b,
    )
    agent = Agent(name="agent", instructions="test", tools=[tool])
    result = AgentLoop(ToolThenFinalModel()).run(agent, "add")

    assert result.answer == "answer: 3"
    assert result.finish_reason == FinishReason.FINAL
    assert any(message.role == "tool" and message.content == "3" for message in result.messages)


def test_unknown_tool_can_stop_on_error() -> None:
    agent = Agent(name="agent", instructions="test")
    result = AgentLoop(UnknownToolModel(), stop_on_tool_error=True).run(agent, "call")

    assert result.finish_reason == FinishReason.TOOL_ERROR
    assert "Tool not found: missing" in result.answer


def test_max_turns() -> None:
    agent = Agent(name="agent", instructions="test")
    result = AgentLoop(UnknownToolModel(), max_turns=2).run(agent, "call")

    assert result.finish_reason == FinishReason.MAX_TURNS
    assert result.turns == 2


def test_runtime_can_be_built_from_pluggable_providers() -> None:
    registry = ProviderRegistry()
    registry.register("model", "echo", lambda options: ContextEchoModel())
    registry.register(
        "memory",
        "local",
        lambda options: LocalMemoryStore(entries=options.get("entries", {})),
    )
    runtime = RuntimeBuilder(registry).build(
        RuntimeConfig(
            model=CapabilityConfig("echo"),
            memory=CapabilityConfig("local", {"entries": {"team": "agent-runtime"}}),
        )
    )
    agent = Agent(name="agent", instructions="base instructions")
    result = AgentLoop(runtime=runtime).run(agent, "hello")

    assert result.finish_reason == FinishReason.FINAL
    assert "base instructions" in result.answer
    assert "Memory:" in result.answer
    assert "team: agent-runtime" in result.answer


def test_runtime_tools_can_come_from_tool_provider() -> None:
    tool = FunctionTool(
        name="add",
        description="Add numbers",
        input_schema={"type": "object"},
        fn=lambda a, b: a + b,
    )
    registry = ProviderRegistry()
    registry.register("model", "tool_then_final", lambda options: ToolThenFinalModel())
    registry.register("tools", "static", lambda options: StaticToolProvider(options["tools"]))
    runtime = RuntimeBuilder(registry).build(
        RuntimeConfig(
            model=CapabilityConfig("tool_then_final"),
            tools=CapabilityConfig("static", {"tools": [tool]}),
        )
    )
    agent = Agent(name="agent", instructions="test")
    result = AgentLoop(runtime=runtime).run(agent, "add")

    assert result.answer == "answer: 3"
