"""What the dashboard is doing, in words (TODO69).

A picture of a system is only as good as what it says about the system's
state. The panels show the numbers; the narration says what they mean and
what just changed, in a sentence a reader — a person, or a model looking at
the screen — can follow without knowing the interface.

The sentences are written here, once, and read by two: the browser renders
them as captions, and an agent reads them over HTTP. A dashboard that
composed its own sentences in the browser would have two vocabularies, and
they would drift.

Every sentence names a run, a cell, a number or a rule. A sentence a reader
cannot check against the panels is a decoration, not a narration.
"""

from __future__ import annotations

import statistics
from collections import deque
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Final

from computronium.experiment.execution.events import STAGE_ACTIONS

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

    from computronium.experiment.execution.events import PipelineEvent

# How many narrated moments the dashboard keeps.
HISTORY = 50

# The axes a cell's label uses, in the order the ontology declares them.
CELL_AXES: Final[tuple[str, ...]] = (
    "substrate",
    "geometry",
    "dynamics",
    "plasticity",
    "credit",
    "update",
)


@dataclass(frozen=True, slots=True)
class Line:
    """One narrated moment: when it happened, what it said, how loud."""

    at: str
    text: str
    level: str = "ok"
    stage: str = ""


def _number(value: Any, places: int = 3) -> str:
    """A number as a reader would read it."""
    if isinstance(value, bool) or not isinstance(value, int | float):
        return str(value)
    return f"{value:.{places}f}"


def _stage_number(stage: str) -> str:
    """The stage's position in the pipeline, when it has one."""
    head = stage.split("_", 1)[0]
    return head[1:] if head.startswith("s") and head[1:].isdigit() else ""


def _cell_label(key: Sequence[str]) -> str:
    """A cell's name, short enough for a caption.

    The credit arm is what a run compares, so it names the cell; the axes the
    run held fixed are in the drawer and the legend, not in a caption.
    """
    credit_at = CELL_AXES.index("credit")
    if credit_at < len(key) and key[credit_at]:
        return key[credit_at]
    return "/".join(value for value in key if value)


def _cell_key(coordinate: Mapping[str, Any]) -> tuple[str, ...]:
    """The cell a record names, as its axis values in the declared order."""
    return tuple(str(coordinate.get(axis, "")) for axis in CELL_AXES)


def measured_cells(
    records: Sequence[Mapping[str, Any]],
) -> dict[tuple[str, ...], list[float]]:
    """The cells the records measured, and what each of them scored."""
    by_cell: dict[tuple[str, ...], list[float]] = {}
    for record in records:
        coordinate = record.get("coordinate") or {}
        payload = record.get("payload") or {}
        value = payload.get("val_acc")
        if not isinstance(value, int | float) or isinstance(value, bool):
            continue
        by_cell.setdefault(_cell_key(coordinate), []).append(float(value))
    return by_cell


def best_cell(
    records: Sequence[Mapping[str, Any]],
) -> tuple[str, float, float, int] | None:
    """The cell that scored highest, and what it scored.

    Returns the cell's name, its mean, its spread and its seed count.
    """
    by_cell = measured_cells(records)
    if not by_cell:
        return None
    key, values = max(by_cell.items(), key=lambda item: statistics.fmean(item[1]))
    spread = statistics.stdev(values) if len(values) > 1 else 0.0
    return _cell_label(key), statistics.fmean(values), spread, len(values)


def event_sentence(event: PipelineEvent, chance: float | None = None) -> str:
    """What one event says, in a sentence a reader can check."""
    stage = event.stage
    detail = event.detail or {}

    if stage == "s7_measure":
        cell = detail.get("cell") or "a cell"
        seed = detail.get("seed")
        parts = [f"Measured {cell}"]
        if seed is not None:
            parts.append(f"seed {seed}")
        sentence = ", ".join(parts)
        metric = detail.get("val_acc")
        if isinstance(metric, int | float) and not isinstance(metric, bool):
            sentence += f": val_acc {_number(metric)}"
        if chance is not None:
            sentence += f" (chance {_number(chance, 2)})"
        return sentence + "."

    if stage == "campaign":
        return f"Campaign {event.message}."

    action = STAGE_ACTIONS.get(stage)
    if action is None:
        return f"{event.message}."

    number = _stage_number(stage)
    where = f"Stage {number} — " if number else ""
    counts: list[str] = []
    if detail.get("proposals"):
        counts.append(f"{detail['proposals']} proposals")
    if detail.get("records"):
        counts.append(f"{detail['records']} records")
    tail = f": {', '.join(counts)}" if counts else ""
    return f"{where}{action}{tail}."


def _run_sentence(run: Mapping[str, Any], metrics: Mapping[str, Any]) -> str:
    """Which run this is, and how much of it exists."""
    where = " · ".join(
        part
        for part in (
            str(run.get("profile") or ""),
            ", ".join(run.get("tasks") or []),
            str(run.get("fidelity") or ""),
        )
        if part
    )
    records = metrics.get("records") or []
    cells = len(measured_cells(records))
    return (
        f"Run {where or run.get('run_id', '?')} — {run.get('mode', 'EXPLORATORY')}. "
        f"{cells} cell{'s' if cells != 1 else ''} measured, {len(records)} records."
    )


def _meaning_sentence(
    metrics: Mapping[str, Any],
    queue: Mapping[str, Any] | None,
) -> str:
    """What the numbers mean, and what the machine is doing."""
    parts: list[str] = []
    best = best_cell(metrics.get("records") or [])
    if best is not None:
        name, mean, spread, seeds = best
        parts.append(
            f"best cell: {name} at {_number(mean)} ± {_number(spread)} (n={seeds})"
        )
    chance = metrics.get("chance")
    if chance is not None:
        parts.append(f"chance {_number(chance, 2)}")
    required = metrics.get("required_seeds") or 0
    if required:
        per_cell = (metrics.get("resources") or {}).get("seeds_per_arm") or 0
        missing = max(0, int(required) - int(per_cell))
        parts.append(
            f"{missing} more seed{'s' if missing != 1 else ''} needed for a claim"
        )
    if queue:
        parts.append(
            f"queue: {queue.get('running', 0)} running, {queue.get('queued', 0)} queued"
        )
    store = metrics.get("store") or {}
    if store.get("source"):
        parts.append(f"picture: {store['source']}")
    return ". ".join(part.capitalize() for part in parts) + "."


def state_sentences(
    metrics: Mapping[str, Any],
    queue: Mapping[str, Any] | None = None,
) -> tuple[str, ...]:
    """What the system is doing right now, in two sentences.

    The first says which run this is and how much of it exists; the second
    says what the numbers mean and what the machine is doing.
    """
    run = metrics.get("run") or {}
    if not run:
        return ("No run has reported yet.", "Waiting for the store to answer.")
    return (_run_sentence(run, metrics), _meaning_sentence(metrics, queue))


class Narration:
    """The dashboard's account of itself.

    The account is a stream of narrated moments and a summary of the present.
    A client that arrives late is given the recent moments, so it can say
    what has been happening without having watched it.
    """

    def __init__(self, history: int = HISTORY) -> None:
        self._lines: deque[Line] = deque(maxlen=history)
        self._state: tuple[str, ...] = ()
        self._chances: dict[str, float] = {}
        self._current_run_id: str | None = None

    @property
    def current_run_id(self) -> str | None:
        """The run the state describes."""
        return self._current_run_id

    def event(self, event: PipelineEvent) -> Line:
        """Narrate one event."""
        chance = self._chances.get(event.run_id or "")
        line = Line(
            at=event.timestamp,
            text=event_sentence(event, chance),
            level=event.level,
            stage=event.stage,
        )
        self._lines.append(line)
        return line

    def state(
        self,
        sentences: Sequence[str],
        *,
        run_id: str | None = None,
        chance: float | None = None,
    ) -> None:
        """Record what the system is doing right now."""
        self._state = tuple(sentences)
        self._current_run_id = run_id
        if run_id and chance is not None:
            self._chances[run_id] = chance

    def lines(self) -> tuple[Line, ...]:
        """The narrated moments, oldest first."""
        return tuple(self._lines)

    def current(self) -> tuple[str, ...]:
        """The sentences that describe the present."""
        return self._state

    def latest(self) -> Line | None:
        """The most recent narrated moment."""
        return self._lines[-1] if self._lines else None

    def script(self) -> str:
        """The whole story, as one block of text.

        The form an agent reads: what is happening, then what has been
        happening, in order.
        """
        parts: list[str] = []
        if self._state:
            parts.append(" ".join(self._state))
        for line in self._lines:
            parts.append(f"[{line.at}] {line.text}")
        return "\n".join(parts)


__all__ = [
    "CELL_AXES",
    "HISTORY",
    "Line",
    "Narration",
    "best_cell",
    "event_sentence",
    "measured_cells",
    "state_sentences",
]
