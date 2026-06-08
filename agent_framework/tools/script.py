from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import TYPE_CHECKING, Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from agent_framework.core.types import ToolCall, ToolResult
from agent_framework.tools.base import Tool, ToolSpec
from agent_framework.tools.providers import ToolProvider

if TYPE_CHECKING:
    from agent_framework.runtime.providers import ProviderRegistry


class ScriptTool(Tool):
    def __init__(self, manifest_tool: dict[str, Any], *, base_dir: Path | None = None) -> None:
        self._name = str(manifest_tool["name"])
        self._description = str(manifest_tool["description"])
        self._input_schema = dict(manifest_tool["input_schema"])
        self._source = dict(manifest_tool["source"])
        self._base_dir = base_dir or Path.cwd()

    def spec(self) -> ToolSpec:
        return ToolSpec(
            name=self._name,
            description=self._description,
            input_schema=self._input_schema,
        )

    def call(self, call: ToolCall) -> ToolResult:
        payload = {
            "name": call.name,
            "arguments": call.arguments,
            "call_id": call.call_id,
        }
        source_type = self._source.get("type")
        if source_type == "local":
            return self._call_local(call, payload)
        if source_type == "http":
            return self._call_http(call, payload)
        return ToolResult(
            call_id=call.call_id,
            name=call.name,
            content=f"Unsupported script tool source type: {source_type}",
            ok=False,
        )

    def _call_local(self, call: ToolCall, payload: dict[str, Any]) -> ToolResult:
        command = self._source.get("command")
        if not isinstance(command, list) or not command:
            return ToolResult(
                call_id=call.call_id,
                name=call.name,
                content="Local script tool requires a non-empty command list.",
                ok=False,
            )

        timeout = float(self._source.get("timeout", 10))
        cwd = self._source.get("cwd")
        if cwd is None:
            cwd_path = self._base_dir
        else:
            cwd_path = self._resolve_path(str(cwd))

        try:
            completed = subprocess.run(
                [str(part) for part in command],
                input=json.dumps(payload),
                text=True,
                capture_output=True,
                timeout=timeout,
                cwd=str(cwd_path),
                check=False,
            )
        except subprocess.TimeoutExpired:
            return ToolResult(
                call_id=call.call_id,
                name=call.name,
                content=f"Local script tool timed out after {timeout:g}s.",
                ok=False,
            )
        except OSError as exc:
            return ToolResult(
                call_id=call.call_id,
                name=call.name,
                content=f"Local script tool failed to start: {exc}",
                ok=False,
            )

        if completed.returncode != 0:
            stderr = completed.stderr.strip()
            return ToolResult(
                call_id=call.call_id,
                name=call.name,
                content=f"Local script tool exited with code {completed.returncode}: {stderr}",
                ok=False,
            )

        return self._parse_response(call, completed.stdout, "Local script tool")

    def _call_http(self, call: ToolCall, payload: dict[str, Any]) -> ToolResult:
        url = self._source.get("url")
        if not isinstance(url, str) or not url:
            return ToolResult(
                call_id=call.call_id,
                name=call.name,
                content="HTTP script tool requires a URL.",
                ok=False,
            )

        timeout = float(self._source.get("timeout", 10))
        headers = {
            "Content-Type": "application/json",
            **dict(self._source.get("headers", {})),
        }
        request = Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST",
        )

        try:
            with urlopen(request, timeout=timeout) as response:
                body = response.read().decode(response.headers.get_content_charset() or "utf-8")
        except (HTTPError, URLError, TimeoutError, OSError) as exc:
            return ToolResult(
                call_id=call.call_id,
                name=call.name,
                content=f"HTTP script tool failed: {exc}",
                ok=False,
            )

        return self._parse_response(call, body, "HTTP script tool")

    def _parse_response(self, call: ToolCall, raw: str, source_label: str) -> ToolResult:
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError as exc:
            return ToolResult(
                call_id=call.call_id,
                name=call.name,
                content=f"{source_label} returned invalid JSON: {exc}",
                ok=False,
            )

        content = str(payload.get("content", ""))
        ok = bool(payload.get("ok", True))
        data = payload.get("data")
        return ToolResult(call_id=call.call_id, name=call.name, content=content, ok=ok, data=data)

    def _resolve_path(self, value: str) -> Path:
        path = Path(value)
        if path.is_absolute():
            return path
        return self._base_dir / path


class ScriptToolProvider(ToolProvider):
    def __init__(self, manifest_path: str | Path) -> None:
        self._manifest_path = Path(manifest_path)
        self._base_dir = self._manifest_path.resolve().parent
        self._tools = self._load_tools()

    def tools_for(self, query: str) -> list[Tool]:
        return list(self._tools)

    def _load_tools(self) -> list[ScriptTool]:
        with self._manifest_path.open("r", encoding="utf-8") as handle:
            manifest = json.load(handle)
        tools = manifest.get("tools", [])
        if not isinstance(tools, list):
            raise ValueError("Script tools manifest requires a top-level 'tools' list.")
        return [ScriptTool(tool, base_dir=self._base_dir) for tool in tools]


def register_script_tools_provider(registry: ProviderRegistry) -> None:
    registry.register(
        "tools",
        "script",
        lambda options: ScriptToolProvider(options["manifest_path"]),
    )
