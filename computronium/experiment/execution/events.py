"""Live pipeline events (TODO68).

The dashboard's live rail renders whatever arrives here. One event shape, one
publish API: producers own the vocabulary, consumers only format.

Events are process-local and best-effort. A subscriber that raises is logged
and skipped — it must never fail the run that produced the event.

An event carries its time twice: as the ISO string a reader sees, and as the
epoch seconds a picture measures. The string has no timezone, so a browser
would have to guess where it was written; the epoch does not need guessing.
"""

from __future__ import annotations

import logging
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Any, Literal

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

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
    at: float = field(default_factory=time.time)

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
            "at": self.at,
        }


@dataclass(frozen=True, slots=True)
class StageSpan:
    """One stage of a run, and the time it took.

    Attributes:
        stage: The stage's id, as the pipeline names it.
        action: What the stage does, in words.
        events: How many times the stage spoke.
        first: When it first spoke, in epoch seconds.
        last: When it last spoke, in epoch seconds.
        offset: Seconds from the run's first event to this stage's first.
        duration: Seconds from this stage's first event to its last.
    """

    stage: str
    action: str
    events: int
    first: float
    last: float
    offset: float
    duration: float


def stage_spans(events: Sequence[Mapping[str, Any]]) -> tuple[StageSpan, ...]:
    """The stages a run went through, in the order it reached them.

    A stage that spoke more than once — a second round, a second batch — is
    one span with a longer reach: the timeline is about the run's shape, not
    about every sentence it said.

    Args:
        events: The event frames, in the order they arrived.

    Returns:
        One span per stage, in the order the stages first spoke.
    """
    spoken: dict[str, list[float]] = {}
    for event in events:
        stage = str(event.get("stage") or "")
        at = event.get("at")
        if not stage or not isinstance(at, int | float) or isinstance(at, bool):
            continue
        spoken.setdefault(stage, []).append(float(at))
    if not spoken:
        return ()

    start = min(times[0] for times in spoken.values())
    return tuple(
        StageSpan(
            stage=stage,
            action=STAGE_ACTIONS.get(stage, stage),
            events=len(times),
            first=min(times),
            last=max(times),
            offset=min(times) - start,
            duration=max(times) - min(times),
        )
        for stage, times in spoken.items()
    )


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
    "StageSpan",
    "get_event_bus",
    "publish_event",
    "set_event_bus",
    "stage_spans",
]
