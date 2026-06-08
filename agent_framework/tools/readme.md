# Tools

This package contains the framework's tool protocol and built-in tool adapters.

## Current Features

- `Tool`: base interface for all callable tools.
- `ToolSpec`: tool metadata exposed to the agent, including `name`, `description`, and `input_schema`.
- `FunctionTool`: wraps a Python callable as a tool.
- `StaticToolProvider`: returns a fixed list of tools.
- `WebSearchTool`: searches the web for current information.
- `WebFetchTool`: fetches a web page and returns readable text.
- `WebToolProvider`: provides both `web_search` and `web_fetch`.
- `ScriptTool`: exposes a user-defined local script or HTTP endpoint as a tool.
- `ScriptToolProvider`: loads user-defined tools from a manifest file.

## Tool Protocol

Every tool implements:

```python
class Tool:
    def spec(self) -> ToolSpec:
        ...

    def call(self, call: ToolCall) -> ToolResult:
        ...
```

`ToolCall.arguments` is a dictionary produced by the model. `ToolResult.content` is the text returned to the model.

## Add a Python Function Tool

```python
from agent_framework.tools import FunctionTool

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
```

## Add Custom Script Tools

Use `ScriptToolProvider` when the tool is implemented outside the framework.

Create a `tools.json` manifest:

```json
{
  "tools": [
    {
      "name": "echo_text",
      "description": "Echo text from a local script.",
      "input_schema": {
        "type": "object",
        "properties": {
          "text": { "type": "string" }
        },
        "required": ["text"]
      },
      "source": {
        "type": "local",
        "command": ["python3", "echo_tool.py"],
        "timeout": 10
      }
    }
  ]
}
```

The local script receives JSON on stdin:

```json
{
  "name": "echo_text",
  "arguments": { "text": "hello" },
  "call_id": "..."
}
```

The local script must print JSON on stdout:

```json
{
  "content": "echo: hello",
  "ok": true,
  "data": { "text": "hello" }
}
```

Register the provider:

```python
from agent_framework.runtime import CapabilityConfig, ProviderRegistry, RuntimeConfig
from agent_framework.tools import register_script_tools_provider

registry = ProviderRegistry()
register_script_tools_provider(registry)

config = RuntimeConfig(
    model=CapabilityConfig("your-model-provider"),
    tools=CapabilityConfig(
        "script",
        {"manifest_path": "examples/script_tools/tools.json"},
    ),
)
```

## Add HTTP Endpoint Tools

For URL-based tools, the framework sends the same JSON payload with HTTP `POST`.

```json
{
  "tools": [
    {
      "name": "remote_lookup",
      "description": "Call a remote lookup service.",
      "input_schema": {
        "type": "object",
        "properties": {
          "query": { "type": "string" }
        },
        "required": ["query"]
      },
      "source": {
        "type": "http",
        "url": "https://example.com/tool",
        "timeout": 10,
        "headers": {
          "Authorization": "Bearer ${TOKEN}"
        }
      }
    }
  ]
}
```

The framework does not download or execute remote code. URL tools are treated as HTTP endpoints.

## Notes

- Tool names must be unique inside a runtime.
- Script tools should write only JSON to stdout.
- Local script failures, timeouts, and invalid JSON responses are returned as `ToolResult(ok=False)`.
- Network tools should be treated as network-risk capabilities by future sandbox and permission policies.
