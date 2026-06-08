from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agent_framework import Agent, AgentLoop
from agent_framework.core.agent import Agent as AgentConfig
from agent_framework.core.model import ModelAdapter
from agent_framework.core.types import Message, ModelOutput, ToolCall
from agent_framework.tools.function import FunctionTool


class ScriptedModel(ModelAdapter):
    """A deterministic model for learning and tests."""

    def generate(self, agent: AgentConfig, messages: list[Message]) -> ModelOutput:
        has_tool_result = any(message.role == "tool" for message in messages)
        if not has_tool_result:
            return ModelOutput(
                content="I need to add two numbers.",
                tool_calls=[
                    ToolCall(name="add", arguments={"a": 2, "b": 3}),
                ],
            )

        result = next(message.content for message in messages if message.role == "tool")
        return ModelOutput(content=f"The answer is {result}.", final=True)


def main() -> None:
    add_tool = FunctionTool(
        name="add",
        description="Add two numbers.",
        input_schema={
            "type": "object",
            "properties": {
                "a": {"type": "number"},
                "b": {"type": "number"},
            },
            "required": ["a", "b"],
        },
        fn=lambda a, b: a + b,
    )
    agent = Agent(
        name="math-agent",
        instructions="Use tools when helpful, then give a final answer.",
        tools=[add_tool],
    )
    loop = AgentLoop(ScriptedModel())
    result = loop.run(agent, "What is 2 + 3?")
    print(result.answer)
    print(result.finish_reason.value)


if __name__ == "__main__":
    main()
