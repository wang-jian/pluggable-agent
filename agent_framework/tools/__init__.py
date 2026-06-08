"""Tool protocol and built-in tools."""

from agent_framework.tools.base import Tool, ToolSpec
from agent_framework.tools.function import FunctionTool
from agent_framework.tools.script import ScriptTool, ScriptToolProvider, register_script_tools_provider
from agent_framework.tools.web import WebFetchTool, WebSearchTool, WebToolProvider

__all__ = [
    "FunctionTool",
    "ScriptTool",
    "ScriptToolProvider",
    "Tool",
    "ToolSpec",
    "WebFetchTool",
    "WebSearchTool",
    "WebToolProvider",
    "register_script_tools_provider",
]
