from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any

from agent_framework.memory.base import MemoryStore

if TYPE_CHECKING:
    from agent_framework.runtime.providers import ProviderRegistry


class OpenVikingMemoryStore(MemoryStore):
    def __init__(
        self,
        *,
        path: str | None = None,
        session_id: str | None = None,
        target_uri: str = "",
        limit: int = 5,
        score_threshold: float | None = None,
        initialize: bool = True,
        auto_commit_on_remember: bool = True,
        client: Any | None = None,
        text_part_type: Any | None = None,
    ) -> None:
        self._target_uri = target_uri
        self._limit = limit
        self._score_threshold = score_threshold
        self._auto_commit_on_remember = auto_commit_on_remember

        if client is None:
            openviking = self._import_openviking()
            if path is None:
                client = openviking.OpenViking()
            else:
                client = openviking.OpenViking(path=path)
            if initialize:
                client.initialize()
        self._client = client
        self._text_part_type = text_part_type or self._load_text_part_type()
        self._session = self._create_session(session_id)

    def start_turn(self, user_input: str) -> None:
        self._add_message("user", user_input)

    def context_for(self, query: str) -> str:
        kwargs: dict[str, Any] = {
            "session": self._session,
            "target_uri": self._target_uri,
            "limit": self._limit,
        }
        if self._score_threshold is not None:
            kwargs["score_threshold"] = self._score_threshold

        results = self._client.search(query, **kwargs)
        contexts = []
        contexts.extend(self._items_for(results, "memories"))
        contexts.extend(self._items_for(results, "resources"))
        contexts.extend(self._items_for(results, "skills"))
        return "\n".join(self._format_context(item) for item in contexts)

    def finish_turn(self, user_input: str, assistant_output: str) -> None:
        self._add_message("assistant", assistant_output)

    def remember(self, key: str, value: str) -> None:
        self._add_message("user", f"Remember [{key}]: {value}")
        if self._auto_commit_on_remember:
            self._session.commit()

    @staticmethod
    def _import_openviking() -> Any:
        try:
            import openviking
        except ImportError as exc:
            raise RuntimeError(
                "OpenViking memory provider requires the optional 'openviking' package. "
                "Install it before using memory:openviking."
            ) from exc
        return openviking

    @staticmethod
    def _load_text_part_type() -> Any | None:
        try:
            from openviking.message import TextPart
        except ImportError:
            return None
        return TextPart

    def _create_session(self, session_id: str | None) -> Any:
        if session_id is None:
            return self._client.session()
        return self._client.session(session_id=session_id)

    def _add_message(self, role: str, content: str) -> None:
        part = self._make_text_part(content)
        self._session.add_message(role, [part])

    def _make_text_part(self, content: str) -> Any:
        if self._text_part_type is None:
            return content
        return self._text_part_type(text=content)

    @staticmethod
    def _items_for(results: Any, name: str) -> list[Any]:
        value = getattr(results, name, None)
        if value is None and isinstance(results, dict):
            value = results.get(name)
        return list(value or [])

    def _format_context(self, item: Any) -> str:
        uri = self._field(item, "uri", "")
        score = self._field(item, "score", None)
        context_type = self._field(item, "context_type", "")
        abstract = self._field(item, "abstract", "")
        prefix_parts = []
        if uri:
            prefix_parts.append(str(uri))
        if context_type:
            prefix_parts.append(str(context_type))
        if score is not None:
            prefix_parts.append(f"score={score}")

        prefix = " | ".join(prefix_parts)
        if prefix and abstract:
            return f"- {prefix}: {abstract}"
        if prefix:
            return f"- {prefix}"
        return f"- {abstract}"

    @staticmethod
    def _field(item: Any, name: str, default: Any) -> Any:
        if isinstance(item, dict):
            return item.get(name, default)
        return getattr(item, name, default)


def register_openviking_memory_provider(registry: ProviderRegistry) -> None:
    registry.register(
        "memory",
        "openviking",
        lambda options: OpenVikingMemoryStore(
            path=options.get("path"),
            session_id=options.get("session_id"),
            target_uri=options.get("target_uri", ""),
            limit=options.get("limit", 5),
            score_threshold=options.get("score_threshold"),
            initialize=options.get("initialize", True),
            auto_commit_on_remember=options.get("auto_commit_on_remember", True),
        ),
    )
