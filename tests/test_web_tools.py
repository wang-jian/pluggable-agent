from __future__ import annotations

from urllib.error import URLError

from agent_framework.core.types import ToolCall
from agent_framework.tools.web import WebClient, WebFetchTool, WebSearchTool, WebToolProvider


class FakeWebClient(WebClient):
    def __init__(self) -> None:
        self.search_calls: list[tuple[str, int]] = []
        self.fetch_calls: list[tuple[str, int]] = []

    def search(self, query: str, *, limit: int) -> list[dict[str, str]]:
        self.search_calls.append((query, limit))
        return [
            {
                "title": "Example result",
                "url": "https://example.com",
                "snippet": "A useful result.",
            }
        ]

    def fetch(self, url: str, *, max_chars: int) -> str:
        self.fetch_calls.append((url, max_chars))
        return "Fetched page text"


class FailingWebClient(WebClient):
    def search(self, query: str, *, limit: int) -> list[dict[str, str]]:
        raise URLError("offline")

    def fetch(self, url: str, *, max_chars: int) -> str:
        raise URLError("offline")


def test_web_search_tool_calls_client_and_formats_results() -> None:
    client = FakeWebClient()
    tool = WebSearchTool(client, default_limit=3)

    result = tool.call(ToolCall(name="web_search", arguments={"query": "agent runtime"}))

    assert result.ok
    assert client.search_calls == [("agent runtime", 3)]
    assert "Example result" in result.content
    assert "https://example.com" in result.content
    assert result.data == [
        {
            "title": "Example result",
            "url": "https://example.com",
            "snippet": "A useful result.",
        }
    ]


def test_web_fetch_tool_calls_client() -> None:
    client = FakeWebClient()
    tool = WebFetchTool(client, default_max_chars=1200)

    result = tool.call(ToolCall(name="web_fetch", arguments={"url": "https://example.com"}))

    assert result.ok
    assert client.fetch_calls == [("https://example.com", 1200)]
    assert result.content == "Fetched page text"


def test_web_tools_report_network_errors() -> None:
    client = FailingWebClient()

    search = WebSearchTool(client).call(ToolCall(name="web_search", arguments={"query": "x"}))
    fetch = WebFetchTool(client).call(ToolCall(name="web_fetch", arguments={"url": "https://x.test"}))

    assert not search.ok
    assert "Web search failed" in search.content
    assert not fetch.ok
    assert "Web fetch failed" in fetch.content


def test_web_tool_provider_returns_search_and_fetch() -> None:
    provider = WebToolProvider(FakeWebClient())

    names = [tool.spec().name for tool in provider.tools_for("anything")]

    assert names == ["web_search", "web_fetch"]
