from __future__ import annotations

import builtins
from dataclasses import dataclass
from typing import Any

from agent_framework.memory.openviking import OpenVikingMemoryStore


@dataclass
class FakeContext:
    uri: str
    context_type: str
    abstract: str
    score: float


class FakeResults:
    def __init__(self) -> None:
        self.memories = [
            FakeContext(
                uri="viking://user/alice/memories/preferences/style.md",
                context_type="memory",
                abstract="Alice prefers concise answers.",
                score=0.9,
            )
        ]
        self.resources = [
            {
                "uri": "viking://resources/project/guide.md",
                "context_type": "resource",
                "abstract": "Project guide.",
                "score": 0.8,
            }
        ]
        self.skills = [
            FakeContext(
                uri="viking://skills/research",
                context_type="skill",
                abstract="Research workflow.",
                score=0.7,
            )
        ]


class FakeTextPart:
    def __init__(self, text: str) -> None:
        self.text = text


class FakeSession:
    def __init__(self) -> None:
        self.messages: list[tuple[str, list[Any]]] = []
        self.commits = 0

    def add_message(self, role: str, parts: list[Any]) -> None:
        self.messages.append((role, parts))

    def commit(self) -> None:
        self.commits += 1


class FakeClient:
    def __init__(self) -> None:
        self.session_calls: list[dict[str, Any]] = []
        self.search_calls: list[dict[str, Any]] = []
        self.session_obj = FakeSession()

    def session(self, **kwargs: Any) -> FakeSession:
        self.session_calls.append(kwargs)
        return self.session_obj

    def search(self, query: str, **kwargs: Any) -> FakeResults:
        self.search_calls.append({"query": query, **kwargs})
        return FakeResults()


def test_openviking_context_for_uses_search_with_session() -> None:
    client = FakeClient()
    memory = OpenVikingMemoryStore(
        client=client,
        text_part_type=FakeTextPart,
        session_id="session-1",
        target_uri="",
        limit=3,
        score_threshold=0.5,
    )

    memory.start_turn("How should I answer?")
    context = memory.context_for("answer style")

    assert client.session_calls == [{"session_id": "session-1"}]
    assert client.search_calls == [
        {
            "query": "answer style",
            "session": client.session_obj,
            "target_uri": "",
            "limit": 3,
            "score_threshold": 0.5,
        }
    ]
    assert client.session_obj.messages[0][0] == "user"
    assert client.session_obj.messages[0][1][0].text == "How should I answer?"
    assert "Alice prefers concise answers." in context
    assert "Project guide." in context
    assert "Research workflow." in context


def test_openviking_finish_turn_writes_assistant_message() -> None:
    client = FakeClient()
    memory = OpenVikingMemoryStore(client=client, text_part_type=FakeTextPart)

    memory.finish_turn("question", "answer")

    assert client.session_obj.messages == [("assistant", [client.session_obj.messages[0][1][0]])]
    assert client.session_obj.messages[0][1][0].text == "answer"


def test_openviking_remember_commits_by_default() -> None:
    client = FakeClient()
    memory = OpenVikingMemoryStore(client=client, text_part_type=FakeTextPart)

    memory.remember("preference", "Use short answers")

    assert client.session_obj.messages[0][0] == "user"
    assert client.session_obj.messages[0][1][0].text == "Remember [preference]: Use short answers"
    assert client.session_obj.commits == 1


def test_openviking_import_error_is_clear() -> None:
    original_import = builtins.__import__

    def fake_import(name: str, *args: Any, **kwargs: Any) -> Any:
        if name == "openviking":
            raise ImportError("missing")
        return original_import(name, *args, **kwargs)

    builtins.__import__ = fake_import
    try:
        try:
            OpenVikingMemoryStore(initialize=False)
        except RuntimeError as exc:
            assert "requires the optional 'openviking' package" in str(exc)
        else:
            raise AssertionError("expected RuntimeError")
    finally:
        builtins.__import__ = original_import
