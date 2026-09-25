"""UX-L16: EventBus delivers every message to subscribed handlers."""

from __future__ import annotations

import asyncio

from computronium.ui.event_bus import (
    ArtifactChanged,
    ConfigChanged,
    EventBus,
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
    config: list[tuple[str, ...]] = []
    bus.subscribe(WebSocketEvent, lambda e: ws.append(e.topic))
    bus.subscribe(ConfigChanged, lambda e: config.append(e.objectives))
    bus.publish(ArtifactChanged(signature=(), root=None))  # type: ignore[arg-type]
    bus.publish(ConfigChanged(objectives=("accuracy",)))
    assert ws == [] and config == [("accuracy",)]


def test_unsubscribe_stops_delivery() -> None:
    bus = EventBus()
    received: list[int] = []
    unsub = bus.subscribe(ConfigChanged, lambda _e: received.append(1))
    bus.publish(ConfigChanged(objectives=("accuracy",)))
    unsub()
    bus.publish(ConfigChanged(objectives=("walltime_s",)))
    assert received == [1]


def test_async_delivery_publish_async() -> None:
    async def main() -> list[str]:
        bus = EventBus()
        received: list[str] = []

        async def handler(event: WebSocketEvent) -> None:  # ruff: ignore[unused-async]
            received.append(event.topic)

        bus.subscribe_async(WebSocketEvent, handler)
        await bus.publish_async(WebSocketEvent(topic="telemetry", payload={}))
        await bus.publish_async(WebSocketEvent(topic="events", payload={}))
        return received

    assert asyncio.run(main()) == ["telemetry", "events"]


def test_handler_exception_isolated() -> None:
    bus = EventBus()
    received: list[tuple[str, ...]] = []

    def bad(_event: ConfigChanged) -> None:
        raise RuntimeError("boom")

    bus.subscribe(ConfigChanged, bad)
    bus.subscribe(ConfigChanged, lambda e: received.append(e.objectives))
    bus.publish(ConfigChanged(objectives=("accuracy",)))
    assert received == [("accuracy",)]
