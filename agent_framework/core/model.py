from __future__ import annotations

from abc import ABC, abstractmethod

from agent_framework.core.agent import Agent
from agent_framework.core.types import Message, ModelOutput


class ModelAdapter(ABC):
    """Model boundary used by AgentLoop.

    A real adapter can wrap OpenAI, Anthropic, or a local model. Keeping this
    interface tiny makes the loop testable without network access.
    """

    @abstractmethod
    def generate(self, agent: Agent, messages: list[Message]) -> ModelOutput:
        raise NotImplementedError
