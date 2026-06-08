"""Tool protocol and built-in tools."""

from agent_framework.tools.base import Tool, ToolSpec
from agent_framework.tools.function import FunctionTool
from agent_framework.tools.web import WebFetchTool, WebSearchTool, WebToolProvider

__all__ = [
    "FunctionTool",
    "Tool",
    "ToolSpec",
    "WebFetchTool",
    "WebSearchTool",
    "WebToolProvider",
]
