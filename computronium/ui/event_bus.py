"""Reactive State Bus (X3) — lightweight asyncio-based EventBus for artifact changes,
websocket events. Panels subscribe to relevant topics.

Decouples producers (poll/WS) from consumers (panels); enables future multi-root,
multi-client.
"""

from __future__ import annotations

import asyncio
import contextlib
from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, cast

if TYPE_CHECKING:
    from pathlib import Path


@dataclass(frozen=True, slots=True)
class Event:
    """Base event class."""


@dataclass(frozen=True, slots=True)
class ArtifactChanged(Event):
    """Artifacts on disk have changed."""

    signature: tuple[tuple[int, int], ...]
    root: Path


@dataclass(frozen=True, slots=True)
class ConfigChanged(Event):
    """Campaign config changed (hot-reload)."""

    objectives: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class WebSocketEvent(Event):
    """Raw WebSocket event received."""

    topic: str  # "telemetry" or "events"
    payload: dict[str, Any]


@dataclass(frozen=True, slots=True)
class WebSocketTelemetry(Event):
    """Parsed telemetry data."""

    loss: float
    step: int
    metrics: dict[str, float]


@dataclass(frozen=True, slots=True)
class WebSocketEvents(Event):
    """Parsed events data."""

    events: list[dict[str, Any]]


@dataclass(frozen=True, slots=True)
class PanelRenderFailed(Event):
    """A dashboard panel failed to render (serves the error-card fallback)."""

    panel_key: str
    error: str


type EventHandler[E: Event] = Callable[[E], Any]
type AsyncEventHandler[E: Event] = Callable[[E], Any]  # Returns awaitable


class EventBus:
    """Lightweight publish/subscribe event bus for dashboard events.

    Handlers are keyed by exact event type at publish time. Internal storage
    is deliberately loose (``object``) because ``EventHandler`` is contravariant
    in its argument; the type is recovered at the dispatch boundary.
    """

    def __init__(self) -> None:
        self._handlers: dict[type[Event], list[object]] = defaultdict(list)
        self._async_handlers: dict[type[Event], list[object]] = defaultdict(list)
        self._loop: asyncio.AbstractEventLoop | None = None

    def _get_loop(self) -> asyncio.AbstractEventLoop:
        """Get or create event loop."""
        try:
            return asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return loop

    def subscribe[E: Event](
        self,
        event_type: type[E],
        handler: EventHandler[E],
    ) -> Callable[[], None]:
        """Subscribe to an event type. Returns unsubscribe function."""
        self._handlers[event_type].append(handler)

        def unsubscribe() -> None:
            self._handlers[event_type].remove(handler)

        return unsubscribe

    def subscribe_async[E: Event](
        self,
        event_type: type[E],
        handler: AsyncEventHandler[E],
    ) -> Callable[[], None]:
        """Subscribe to an event type with async handler. Returns unsubscribe function."""
        self._async_handlers[event_type].append(handler)

        def unsubscribe() -> None:
            self._async_handlers[event_type].remove(handler)

        return unsubscribe

    def publish(self, event: Event) -> None:
        """Publish an event to all subscribers (sync)."""
        # Sync handlers
        for handler in self._handlers[type(event)]:
            with contextlib.suppress(Exception):
                cast("EventHandler[Event]", handler)(event)

        # Async handlers - schedule on event loop
        loop = self._get_loop()
        for handler in self._async_handlers[type(event)]:
            with contextlib.suppress(Exception):
                loop.create_task(cast("AsyncEventHandler[Event]", handler)(event))

    async def publish_async(self, event: Event) -> None:
        """Publish an event to all subscribers (async)."""
        # Sync handlers
        for handler in self._handlers[type(event)]:
            with contextlib.suppress(Exception):
                cast("EventHandler[Event]", handler)(event)

        # Async handlers
        for handler in self._async_handlers[type(event)]:
            await cast("AsyncEventHandler[Event]", handler)(event)

    def clear(self) -> None:
        """Clear all subscriptions (for testing)."""
        self._handlers.clear()
        self._async_handlers.clear()


# Global event bus instance
event_bus = EventBus()
