from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4


@dataclass(frozen=True)
class Event:
    type: str
    payload: dict[str, Any] = field(default_factory=dict)
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())


class EventSink:
    def emit(self, event_type: str, **payload: Any) -> None:
        raise NotImplementedError


class InMemoryEventSink(EventSink):
    def __init__(self) -> None:
        self.events: list[Event] = []

    def emit(self, event_type: str, **payload: Any) -> None:
        self.events.append(Event(type=event_type, payload=payload))
