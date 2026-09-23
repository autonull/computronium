"""UX-L16: EventBus delivers every message to subscribed handlers."""

from __future__ import annotations

import asyncio

from computronium.ui.event_bus import (
    ArtifactChanged,
    EventBus,
    ModeChanged,
    WebSocketEvent,
)


def test_sync_delivery_exact_type() -> None:
    bus = EventBus()
    received: list[str] = []
    bus.subscribe(WebSocketEvent, lambda e: received.append(e.topic))
    bus.publish(WebSocketEvent(topic="events", payload={}))
    bus.publish(WebSocketEvent(topic="telemetry", payload={}))
    assert received == ["events", "telemetry"]


def test_subscription_isolation_by_type() -> None:
    bus = EventBus()
    ws: list[str] = []
    mode: list[str] = []
    bus.subscribe(WebSocketEvent, lambda e: ws.append(e.topic))
    bus.subscribe(ModeChanged, lambda e: mode.append(e.mode))
    bus.publish(ArtifactChanged(signature=(), root=None))  # type: ignore[arg-type]
    bus.publish(ModeChanged(mode="lab"))
    assert ws == [] and mode == ["lab"]


def test_unsubscribe_stops_delivery() -> None:
    bus = EventBus()
    received: list[int] = []
    unsub = bus.subscribe(ModeChanged, lambda _e: received.append(1))
    bus.publish(ModeChanged(mode="lab"))
    unsub()
    bus.publish(ModeChanged(mode="explorer"))
    assert received == [1]


def test_async_delivery_publish_async() -> None:
    async def main() -> list[str]:
        bus = EventBus()
        received: list[str] = []

        async def handler(event: WebSocketEvent) -> None:  # noqa: RUF029
            received.append(event.topic)

        bus.subscribe_async(WebSocketEvent, handler)
        await bus.publish_async(WebSocketEvent(topic="telemetry", payload={}))
        await bus.publish_async(WebSocketEvent(topic="events", payload={}))
        return received

    assert asyncio.run(main()) == ["telemetry", "events"]


def test_handler_exception_isolated() -> None:
    bus = EventBus()
    received: list[str] = []

    def bad(_event: ModeChanged) -> None:
        raise RuntimeError("boom")

    bus.subscribe(ModeChanged, bad)
    bus.subscribe(ModeChanged, lambda e: received.append(e.mode))
    bus.publish(ModeChanged(mode="lab"))
    assert received == ["lab"]
