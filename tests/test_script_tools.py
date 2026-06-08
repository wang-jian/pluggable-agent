from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path
from typing import Any

from agent_framework.core.types import ToolCall
from agent_framework.runtime import CapabilityConfig, ProviderRegistry, RuntimeBuilder, RuntimeConfig
from agent_framework.tools.script import ScriptToolProvider, register_script_tools_provider


def test_script_tool_provider_loads_manifest_specs() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        manifest = root / "tools.json"
        manifest.write_text(
            json.dumps(
                {
                    "tools": [
                        {
                            "name": "hello",
                            "description": "Say hello.",
                            "input_schema": {"type": "object"},
                            "source": {"type": "local", "command": [sys.executable, "hello.py"]},
                        }
                    ]
                }
            ),
            encoding="utf-8",
        )

        provider = ScriptToolProvider(manifest)
        specs = [tool.spec() for tool in provider.tools_for("hello")]

    assert specs[0].name == "hello"
    assert specs[0].description == "Say hello."
    assert specs[0].input_schema == {"type": "object"}


def test_local_script_tool_uses_json_stdin_stdout() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        script = root / "echo.py"
        script.write_text(
            "import json, sys\n"
            "payload = json.loads(sys.stdin.read())\n"
            "text = payload['arguments']['text']\n"
            "print(json.dumps({'content': 'echo: ' + text, 'ok': True, 'data': {'call_id': payload['call_id']}}))\n",
            encoding="utf-8",
        )
        manifest = _write_manifest(
            root,
            {
                "type": "local",
                "command": [sys.executable, "echo.py"],
            },
        )
        tool = ScriptToolProvider(manifest).tools_for("")[0]

        result = tool.call(ToolCall(name="custom_echo", arguments={"text": "hello"}, call_id="call-1"))

    assert result.ok
    assert result.content == "echo: hello"
    assert result.data == {"call_id": "call-1"}


def test_http_script_tool_posts_json_and_reads_response() -> None:
    seen: dict[str, Any] = {}

    class FakeHeaders:
        def get_content_charset(self) -> str:
            return "utf-8"

    class FakeResponse:
        headers = FakeHeaders()

        def __enter__(self) -> "FakeResponse":
            return self

        def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
            return None

        def read(self) -> bytes:
            return json.dumps({"content": "remote ok", "ok": True, "data": {"remote": True}}).encode(
                "utf-8"
            )

    def fake_urlopen(request: Any, timeout: float) -> FakeResponse:
        seen["url"] = request.full_url
        seen["payload"] = json.loads(request.data.decode("utf-8"))
        seen["timeout"] = timeout
        return FakeResponse()

    import agent_framework.tools.script as script_module

    original_urlopen = script_module.urlopen
    script_module.urlopen = fake_urlopen
    try:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = _write_manifest(
                root,
                {
                    "type": "http",
                    "url": "https://example.com/tool",
                    "timeout": 3,
                },
            )
            tool = ScriptToolProvider(manifest).tools_for("")[0]

            result = tool.call(ToolCall(name="custom_echo", arguments={"text": "hello"}, call_id="call-2"))
    finally:
        script_module.urlopen = original_urlopen

    assert result.ok
    assert result.content == "remote ok"
    assert result.data == {"remote": True}
    assert seen["url"] == "https://example.com/tool"
    assert seen["timeout"] == 3
    assert seen["payload"] == {
        "name": "custom_echo",
        "arguments": {"text": "hello"},
        "call_id": "call-2",
    }


def test_local_script_tool_reports_errors() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        bad_json = root / "bad_json.py"
        bad_json.write_text("print('not-json')\n", encoding="utf-8")
        failing = root / "failing.py"
        failing.write_text("import sys\nprint('boom', file=sys.stderr)\nsys.exit(2)\n", encoding="utf-8")

        bad_tool = ScriptToolProvider(
            _write_manifest(root, {"type": "local", "command": [sys.executable, "bad_json.py"]})
        ).tools_for("")[0]
        failing_tool = ScriptToolProvider(
            _write_manifest(root, {"type": "local", "command": [sys.executable, "failing.py"]})
        ).tools_for("")[0]

        bad_result = bad_tool.call(ToolCall(name="custom_echo", arguments={}))
        failing_result = failing_tool.call(ToolCall(name="custom_echo", arguments={}))

    assert not bad_result.ok
    assert "invalid JSON" in bad_result.content
    assert not failing_result.ok
    assert "exited with code 2" in failing_result.content


def test_script_tools_provider_can_be_registered() -> None:
    registry = ProviderRegistry()
    registry.register("model", "dummy", lambda options: object())
    register_script_tools_provider(registry)

    with tempfile.TemporaryDirectory() as tmp:
        manifest = _write_manifest(
            Path(tmp),
            {
                "type": "local",
                "command": [sys.executable, "missing.py"],
            },
        )
        runtime = RuntimeBuilder(registry).build(
            RuntimeConfig(
                model=CapabilityConfig("dummy"),
                tools=CapabilityConfig("script", {"manifest_path": str(manifest)}),
            )
        )

    assert [tool.spec().name for tool in runtime.tools.tools_for("")] == ["custom_echo"]


def _write_manifest(root: Path, source: dict[str, Any]) -> Path:
    manifest = root / "tools.json"
    manifest.write_text(
        json.dumps(
            {
                "tools": [
                    {
                        "name": "custom_echo",
                        "description": "Custom echo tool.",
                        "input_schema": {
                            "type": "object",
                            "properties": {"text": {"type": "string"}},
                        },
                        "source": source,
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    return manifest
