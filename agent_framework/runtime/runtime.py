from __future__ import annotations

from dataclasses import dataclass, field

from agent_framework.core.agent import Agent
from agent_framework.core.model import ModelAdapter
from agent_framework.core.types import Message
from agent_framework.memory.base import MemoryStore, NullMemoryStore
from agent_framework.mcp.base import MCPClient, NullMCPClient
from agent_framework.rag.base import NullRAGEngine, RAGEngine
from agent_framework.skills.base import NullSkillLoader, SkillLoader
from agent_framework.tools.base import Tool
from agent_framework.tools.providers import NullToolProvider, ToolProvider


@dataclass
class AgentRuntime:
    model: ModelAdapter
    memory: MemoryStore = field(default_factory=NullMemoryStore)
    rag: RAGEngine = field(default_factory=NullRAGEngine)
    mcp: MCPClient = field(default_factory=NullMCPClient)
    skills: SkillLoader = field(default_factory=NullSkillLoader)
    tools: ToolProvider = field(default_factory=NullToolProvider)

    def build_messages(self, agent: Agent, user_input: str) -> list[Message]:
        context_parts = []
        memory_context = self.memory.context_for(user_input)
        rag_context = self.rag.context_for(user_input)
        skill_context = self.skills.instructions_for(user_input)

        if memory_context:
            context_parts.append(f"Memory:\n{memory_context}")
        if rag_context:
            context_parts.append(f"Knowledge:\n{rag_context}")
        if skill_context:
            context_parts.append(f"Skills:\n{skill_context}")

        instructions = agent.instructions
        if context_parts:
            instructions = f"{instructions}\n\n" + "\n\n".join(context_parts)

        return [
            Message(role="system", content=instructions),
            Message(role="user", content=user_input),
        ]

    def build_tools(self, agent: Agent, user_input: str) -> list[Tool]:
        tools = list(agent.tools)
        tools.extend(self.tools.tools_for(user_input))
        tools.extend(self.mcp.tools_for(user_input))
        tools.extend(self.skills.tools_for(user_input))
        return tools
