"""What the dashboard is doing, in words (TODO69).

A picture of a system is only as good as what it says about the system's
state. The panels show the numbers; the narration says what they *mean* —
which run this is, what it has found, what is still open — in a sentence a
reader, or a model looking at the screen, can follow without knowing the
interface.

The narration speaks in words, not in figures. It does not read out an
accuracy or a seed count: those are on the panels, and a voice-over that
recites them is worse than useless. What it says is the *shape* of what is
happening — the run is exploring, one arm is ahead of the others, the claim
cannot be made yet, the queue is idle — and every claim it makes can be
checked against the picture.

The sentences are written here, once, and read by two: the browser renders
them as captions, and an agent reads them over HTTP. A dashboard that
composed its own sentences in the browser would have two vocabularies, and
they would drift.
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

# The stages whose verb does not take the usual "-ing".
_PARTICIPLES: Final[dict[str, str]] = {"write": "writing"}


@dataclass(frozen=True, slots=True)
class Line:
    """One narrated moment: when it happened, what it said, how loud."""

    at: str
    text: str
    level: str = "ok"
    stage: str = ""


def _gerund(action: str) -> str:
    """What a stage is doing, said in the present tense."""
    verb, _, rest = action.partition(" ")
    participle = _PARTICIPLES.get(verb, f"{verb}ing")
    phrase = f"{participle} {rest}".strip()
    return phrase[:1].upper() + phrase[1:]


def _arm_from_cell(cell: str) -> str:
    """The arm a measured cell belongs to: the credit primitive that names it."""
    head = cell.split("/", 1)[0].strip()
    return head if head else ""


def _arm_from_key(key: Sequence[str]) -> str:
    """The arm a cell belongs to, from the cell's axis values."""
    credit_at = CELL_AXES.index("credit")
    return key[credit_at] if credit_at < len(key) else ""


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

    Returns the cell's arm, its mean, its spread and its seed count. The
    figures are the panels' business; the narration asks only which arm
    leads.
    """
    by_cell = measured_cells(records)
    if not by_cell:
        return None
    key, values = max(by_cell.items(), key=lambda item: statistics.fmean(item[1]))
    spread = statistics.stdev(values) if len(values) > 1 else 0.0
    return _arm_from_key(key), statistics.fmean(values), spread, len(values)


def event_sentence(event: PipelineEvent) -> str:
    """What one event says, in a sentence a reader can check."""
    stage = event.stage
    detail = event.detail or {}

    if stage == "s7_measure":
        arm = _arm_from_cell(str(detail.get("cell") or ""))
        return f"Measured the {arm} arm." if arm else "Measured a cell."

    if stage == "campaign":
        return f"A campaign {_campaign_verb(event.message)}."

    action = STAGE_ACTIONS.get(stage)
    if action is None:
        return f"{event.message}."

    if event.level == "error":
        return f"The pipeline could not {action}."
    return f"{_gerund(action)}."


def _campaign_verb(message: str) -> str:
    """What happened to a campaign, in words."""
    head = message.split(" ", 1)[0].lower()
    return {
        "queued": "was queued",
        "started": "started",
        "completed": "finished",
        "failed": "failed",
        "cancelled": "was cancelled",
        "preempted": "was preempted",
    }.get(head, "changed")


def _run_sentence(run: Mapping[str, Any], metrics: Mapping[str, Any]) -> str:
    """Which run this is, and how far it has got."""
    profile = str(run.get("profile") or "")
    tasks = ", ".join(run.get("tasks") or [])
    if profile and tasks:
        subject = f"{profile} run on {tasks}"
    elif profile:
        subject = f"{profile} run"
    elif tasks:
        subject = f"run on {tasks}"
    else:
        subject = "run"
    mode = str(run.get("mode") or "EXPLORATORY").lower()
    sentence = f"The {subject} is {mode}"

    records = metrics.get("records") or []
    measured = len(measured_cells(records))
    declared = run.get("declared_cells") or 0
    if not measured:
        sentence += " and has measured nothing yet"
    elif declared and measured >= declared:
        sentence += " and has measured every cell it declared"
    else:
        sentence += " and part-way through the space it declared"

    if str(run.get("status") or "").lower() == "running":
        sentence += ". It is still running"
    return sentence + "."


def _evidence_sentence(metrics: Mapping[str, Any]) -> str:
    """What the evidence says, in words."""
    records = metrics.get("records") or []
    if not records:
        # The run's own sentence already says that nothing was measured.
        # Saying it twice is how a voice-over starts to sound like a form.
        return ""
    best = best_cell(records)
    if best is None:
        return "One cell is ahead of the others."
    arm, mean, _spread, _seeds = best
    if not arm:
        return "One cell is ahead of the others."
    chance = metrics.get("chance")
    sentence = f"The {arm} arm is ahead of the others"
    if chance is not None:
        sentence += " and beats chance" if mean > chance else " but is not above chance"
    return sentence + "."


def _claim_sentence(metrics: Mapping[str, Any]) -> str:
    """Whether the evidence can carry a claim."""
    required = metrics.get("required_seeds") or 0
    if not required:
        return ""
    per_cell = (metrics.get("resources") or {}).get("seeds_per_arm") or 0
    if per_cell >= required:
        return "The claim can be made: the seeds are there."
    return "The claim cannot be made yet: too few seeds."


def _queue_sentence(queue: Mapping[str, Any] | None) -> str:
    """What the machine is doing."""
    if not queue:
        return ""
    if queue.get("running"):
        return "A campaign is running."
    if queue.get("queued"):
        return "Campaigns are waiting to run."
    return "The queue is idle."


def control_sentence(control: Mapping[str, Any] | None) -> str:
    """What the run has been asked to do, in words.

    The verbs are the *shape* of the run's state — paused, stopped — and
    nothing more: the ceiling and the counts are on the panels, and a
    sentence that recites them is worse than useless.
    """
    if not control:
        return ""
    if control.get("cancel"):
        return "The run has been stopped."
    if control.get("paused"):
        return "The run is paused."
    return ""


def state_sentences(
    metrics: Mapping[str, Any],
    queue: Mapping[str, Any] | None = None,
    control: Mapping[str, Any] | None = None,
) -> tuple[str, ...]:
    """What the system is doing right now, in two sentences.

    The first says which run this is and how far it has got; the second says
    what it has found, what it cannot yet say, and what the machine is doing.
    """
    run = metrics.get("run") or {}
    if not run:
        return (
            "No run has reported yet.",
            "The dashboard is waiting for the store to answer.",
        )
    parts = [
        _evidence_sentence(metrics),
        _claim_sentence(metrics),
        _queue_sentence(queue),
        control_sentence(control),
    ]
    return (_run_sentence(run, metrics), " ".join(part for part in parts if part))


class Narration:
    """The dashboard's account of itself.

    The account is a stream of narrated moments and a summary of the present.
    A client that arrives late is given the recent moments, so it can say
    what has been happening without having watched it.
    """

    def __init__(self, history: int = HISTORY) -> None:
        self._lines: deque[Line] = deque(maxlen=history)
        self._state: tuple[str, ...] = ()
        self._current_run_id: str | None = None

    @property
    def current_run_id(self) -> str | None:
        """The run the state describes."""
        return self._current_run_id

    def event(self, event: PipelineEvent) -> Line:
        """Narrate one event."""
        line = Line(
            at=event.timestamp,
            text=event_sentence(event),
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
    ) -> None:
        """Record what the system is doing right now."""
        self._state = tuple(sentences)
        self._current_run_id = run_id

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
    "control_sentence",
    "event_sentence",
    "measured_cells",
    "state_sentences",
]
