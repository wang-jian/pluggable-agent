from __future__ import annotations

import json
from html.parser import HTMLParser
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote_plus
from urllib.request import Request, urlopen

from agent_framework.core.types import ToolCall, ToolResult
from agent_framework.tools.base import Tool, ToolSpec
from agent_framework.tools.providers import ToolProvider


class WebClient:
    def search(self, query: str, *, limit: int) -> list[dict[str, str]]:
        raise NotImplementedError

    def fetch(self, url: str, *, max_chars: int) -> str:
        raise NotImplementedError


class DuckDuckGoWebClient(WebClient):
    def __init__(self, *, timeout: float = 10.0, user_agent: str = "pluggable-agent/0.1") -> None:
        self._timeout = timeout
        self._user_agent = user_agent

    def search(self, query: str, *, limit: int) -> list[dict[str, str]]:
        url = f"https://api.duckduckgo.com/?q={quote_plus(query)}&format=json&no_html=1"
        payload = json.loads(self._read_url(url, max_chars=200_000))
        results: list[dict[str, str]] = []

        abstract_url = payload.get("AbstractURL")
        if abstract_url:
            results.append(
                {
                    "title": payload.get("Heading") or abstract_url,
                    "url": abstract_url,
                    "snippet": payload.get("AbstractText") or "",
                }
            )

        for topic in payload.get("RelatedTopics", []):
            self._collect_topic(topic, results)
            if len(results) >= limit:
                break

        return results[:limit]

    def fetch(self, url: str, *, max_chars: int) -> str:
        raw = self._read_url(url, max_chars=max_chars * 5)
        text = _html_to_text(raw)
        return text[:max_chars]

    def _read_url(self, url: str, *, max_chars: int) -> str:
        request = Request(url, headers={"User-Agent": self._user_agent})
        with urlopen(request, timeout=self._timeout) as response:
            charset = response.headers.get_content_charset() or "utf-8"
            return response.read(max_chars).decode(charset, errors="replace")

    @staticmethod
    def _collect_topic(topic: dict[str, Any], results: list[dict[str, str]]) -> None:
        if "Topics" in topic:
            for nested in topic.get("Topics", []):
                DuckDuckGoWebClient._collect_topic(nested, results)
            return

        url = topic.get("FirstURL")
        if not url:
            return
        results.append(
            {
                "title": topic.get("Text") or url,
                "url": url,
                "snippet": topic.get("Text") or "",
            }
        )


class WebSearchTool(Tool):
    def __init__(self, client: WebClient | None = None, *, default_limit: int = 5) -> None:
        self._client = client or DuckDuckGoWebClient()
        self._default_limit = default_limit

    def spec(self) -> ToolSpec:
        return ToolSpec(
            name="web_search",
            description="Search the web for current information.",
            input_schema={
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "limit": {"type": "integer", "minimum": 1, "maximum": 10},
                },
                "required": ["query"],
            },
        )

    def call(self, call: ToolCall) -> ToolResult:
        query = str(call.arguments["query"])
        limit = int(call.arguments.get("limit", self._default_limit))
        try:
            results = self._client.search(query, limit=limit)
        except (HTTPError, URLError, TimeoutError, OSError) as exc:
            return ToolResult(
                call_id=call.call_id,
                name=call.name,
                content=f"Web search failed: {exc}",
                ok=False,
            )

        return ToolResult(
            call_id=call.call_id,
            name=call.name,
            content=_format_search_results(results),
            ok=True,
            data=results,
        )


class WebFetchTool(Tool):
    def __init__(self, client: WebClient | None = None, *, default_max_chars: int = 8000) -> None:
        self._client = client or DuckDuckGoWebClient()
        self._default_max_chars = default_max_chars

    def spec(self) -> ToolSpec:
        return ToolSpec(
            name="web_fetch",
            description="Fetch a web page and return readable text.",
            input_schema={
                "type": "object",
                "properties": {
                    "url": {"type": "string"},
                    "max_chars": {"type": "integer", "minimum": 200, "maximum": 20000},
                },
                "required": ["url"],
            },
        )

    def call(self, call: ToolCall) -> ToolResult:
        url = str(call.arguments["url"])
        max_chars = int(call.arguments.get("max_chars", self._default_max_chars))
        try:
            content = self._client.fetch(url, max_chars=max_chars)
        except (HTTPError, URLError, TimeoutError, OSError) as exc:
            return ToolResult(
                call_id=call.call_id,
                name=call.name,
                content=f"Web fetch failed: {exc}",
                ok=False,
            )

        return ToolResult(call_id=call.call_id, name=call.name, content=content, ok=True, data=content)


class WebToolProvider(ToolProvider):
    def __init__(self, client: WebClient | None = None) -> None:
        self._client = client or DuckDuckGoWebClient()

    def tools_for(self, query: str) -> list[Tool]:
        return [
            WebSearchTool(self._client),
            WebFetchTool(self._client),
        ]


def _format_search_results(results: list[dict[str, str]]) -> str:
    if not results:
        return "No web search results found."
    lines = []
    for index, result in enumerate(results, start=1):
        title = result.get("title") or result.get("url") or "Untitled"
        url = result.get("url") or ""
        snippet = result.get("snippet") or ""
        lines.append(f"{index}. {title}\nURL: {url}\nSnippet: {snippet}")
    return "\n\n".join(lines)


class _TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []
        self._skip_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"script", "style", "noscript"}:
            self._skip_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "noscript"} and self._skip_depth:
            self._skip_depth -= 1

    def handle_data(self, data: str) -> None:
        if self._skip_depth:
            return
        text = data.strip()
        if text:
            self.parts.append(text)


def _html_to_text(html: str) -> str:
    parser = _TextExtractor()
    parser.feed(html)
    return "\n".join(parser.parts)
