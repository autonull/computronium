"""Live pipeline events (TODO68).

The dashboard's live rail renders whatever arrives here. One event shape, one
publish API: producers own the vocabulary, consumers only format.

Events are process-local and best-effort. A subscriber that raises is logged
and skipped — it must never fail the run that produced the event.
"""

from __future__ import annotations

import logging
import threading
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Literal

logger = logging.getLogger(__name__)

EventLevel = Literal["ok", "warn", "error"]

# The verb each stage reports itself with. The live rail reads as a sequence of
# actions, so the stage id alone ("s5_compose") says less than the action does.
STAGE_ACTIONS: dict[str, str] = {
    "s1_frame": "frame the objective",
    "s2_space": "map the axis space",
    "s3_schedule": "schedule cells",
    "s4_gate": "gate proposals",
    "s5_compose": "compose systems",
    "s6_train": "train cells",
    "s7_measure": "measure cells",
    "s8_record": "record evidence",
    "s9_attribute": "attribute axes",
    "s10_decide": "decide the next round",
    "s11_report": "write the report",
}


@dataclass(frozen=True, slots=True)
class PipelineEvent:
    """One thing that happened, addressed to the stage that did it."""

    stage: str
    message: str
    level: EventLevel = "ok"
    run_id: str | None = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    detail: dict[str, Any] = field(default_factory=dict)

    def to_message(self) -> dict[str, Any]:
        """The dashboard payload for this event."""
        return {
            "type": "pipeline_event",
            "stage": self.stage,
            "message": self.message,
            "level": self.level,
            "run_id": self.run_id,
            "timestamp": self.timestamp,
            "detail": self.detail,
        }


EventListener = Callable[[PipelineEvent], None]


class PipelineEventBus:
    """Thread-safe fan-out of pipeline events to live subscribers."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._listeners: list[EventListener] = []

    def publish(self, event: PipelineEvent) -> None:
        """Deliver an event to every subscriber."""
        with self._lock:
            listeners = tuple(self._listeners)
        for listener in listeners:
            try:
                listener(event)
            except Exception:
                logger.exception("Pipeline event listener failed for %s", event.stage)

    def subscribe(self, listener: EventListener) -> Callable[[], None]:
        """Register a listener; returns the callable that unsubscribes it."""
        with self._lock:
            self._listeners.append(listener)

        def unsubscribe() -> None:
            with self._lock:
                if listener in self._listeners:
                    self._listeners.remove(listener)

        return unsubscribe


class _BusHolder:
    bus: PipelineEventBus | None = None


def get_event_bus() -> PipelineEventBus:
    """The process-wide event bus."""
    if _BusHolder.bus is None:
        _BusHolder.bus = PipelineEventBus()
    return _BusHolder.bus


def set_event_bus(bus: PipelineEventBus | None) -> None:
    """Replace the process-wide event bus (tests pass None to reset)."""
    _BusHolder.bus = bus


def publish_event(
    stage: str,
    message: str,
    *,
    level: EventLevel = "ok",
    run_id: str | None = None,
    detail: dict[str, Any] | None = None,
) -> PipelineEvent:
    """Publish an event on the process-wide bus."""
    event = PipelineEvent(
        stage=stage,
        message=message,
        level=level,
        run_id=run_id,
        detail=detail or {},
    )
    get_event_bus().publish(event)
    return event


__all__ = [
    "STAGE_ACTIONS",
    "EventLevel",
    "EventListener",
    "PipelineEvent",
    "PipelineEventBus",
    "get_event_bus",
    "publish_event",
    "set_event_bus",
]
