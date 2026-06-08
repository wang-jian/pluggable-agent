from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agent_framework import Agent, AgentLoop
from agent_framework.core.agent import Agent as AgentConfig
from agent_framework.core.model import ModelAdapter
from agent_framework.core.types import Message, ModelOutput
from agent_framework.memory.local import LocalMemoryStore
from agent_framework.runtime import CapabilityConfig, ProviderRegistry, RuntimeBuilder, RuntimeConfig
from agent_framework.tools.function import FunctionTool
from agent_framework.tools.providers import StaticToolProvider


class EchoContextModel(ModelAdapter):
    def generate(self, agent: AgentConfig, messages: list[Message]) -> ModelOutput:
        system_message = messages[0].content
        return ModelOutput(content=system_message, final=True)


def main() -> None:
    registry = ProviderRegistry()
    registry.register("model", "local_echo", lambda options: EchoContextModel())
    registry.register(
        "memory",
        "local",
        lambda options: LocalMemoryStore(entries=options.get("entries", {})),
    )
    registry.register(
        "tools",
        "static",
        lambda options: StaticToolProvider(options.get("tools", [])),
    )

    add_tool = FunctionTool(
        name="add",
        description="Add two numbers.",
        input_schema={"type": "object"},
        fn=lambda a, b: a + b,
    )
    config = RuntimeConfig(
        model=CapabilityConfig("local_echo"),
        memory=CapabilityConfig(
            "local",
            options={"entries": {"project": "all capabilities are pluggable"}},
        ),
        tools=CapabilityConfig("static", options={"tools": [add_tool]}),
    )
    runtime = RuntimeBuilder(registry).build(config)
    agent = Agent(name="runtime-agent", instructions="You are a configurable agent.")
    result = AgentLoop(runtime=runtime).run(agent, "show runtime context")
    print(result.answer)


if __name__ == "__main__":
    main()
