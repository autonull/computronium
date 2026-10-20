"""What the dashboard can do with a cell (TODO68).

Reading a cell's evidence is the easy half of a dashboard. These are the
three verbs that turn a cell into work: measure the seeds it still owes,
register the protocol a confirming run must meet, and adopt an unmeasured
cell as a question to answer.

Every verb writes through machinery the system already has — the campaign
queue for work, the pre-registration contract for governance — so the
dashboard never invents a second way to run a cell or a second way to
register a claim.
"""

from __future__ import annotations

import json
import logging
import statistics
from dataclasses import dataclass
from datetime import date, datetime
from typing import TYPE_CHECKING, Any

from computronium.experiment.schema.axis import StructuralAxis
from computronium.experiment.schema.run_spec import AxisSelection, RunSpec
from computronium.validation.preregistration import ThresholdRegistration

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence
    from pathlib import Path

    from computronium.experiment.schema.record import Record

logger = logging.getLogger(__name__)

# The deadline is a hard stop: a replication that reaches it loses the seeds
# it has not measured. The headroom is the room for the machine to be slower
# than it was when the cell was measured.
BUDGET_HEADROOM = 1.5

# The objective a cell's claim is about when the run names none.
ACCURACY_OBJECTIVE = "validation_accuracy"

# The kinds of registration the dashboard writes. A confirmation registers the
# effect a cell already showed; a quest registers the question an unmeasured
# cell answers.
KIND_CONFIRMATION = "confirmation"
KIND_QUEST = "quest"


class ActionUnavailableError(RuntimeError):
    """The action cannot be carried out here."""


@dataclass(frozen=True, slots=True)
class CellTarget:
    """The cell an action is about."""

    run_id: str
    coordinate: Mapping[str, str]

    def axes(self) -> tuple[AxisSelection, ...]:
        """The cell's coordinate as the run's own axis selections."""
        selections = []
        for axis in StructuralAxis:
            value = self.coordinate.get(axis.value, "")
            if value:
                selections.append(AxisSelection(axis=axis, primitives=(value,)))
        return tuple(selections)

    def slug(self) -> str:
        """A name that says which cell this is."""
        parts = [
            f"{axis.value}-{self.coordinate.get(axis.value, '')}"
            for axis in StructuralAxis
            if self.coordinate.get(axis.value, "")
        ]
        return "_".join(parts)

    def describe(self) -> str:
        """The cell in words: every axis, named."""
        return ", ".join(
            f"{axis.value}={self.coordinate.get(axis.value, '')}"
            for axis in StructuralAxis
            if self.coordinate.get(axis.value, "")
        )


@dataclass(frozen=True, slots=True)
class CellEvidence:
    """What the store holds about one cell."""

    measured_seeds: int
    mean: float
    spread: float
    walltime_s: float
    task_id: str

    @property
    def measured(self) -> bool:
        """Whether the cell carries any measurement at all."""
        return self.measured_seeds > 0


def records_for_cell(
    records: Sequence[Record],
    coordinate: Mapping[str, str],
) -> list[Record]:
    """The records that measured one cell."""
    return [
        record
        for record in records
        if all(
            getattr(record, axis.value, "") == coordinate.get(axis.value, "")
            for axis in StructuralAxis
        )
    ]


def cell_evidence(records: Sequence[Record], metric: str) -> CellEvidence:
    """What a cell's records say about it."""
    values = [
        float(record.payload[metric])
        for record in records
        if isinstance(record.payload.get(metric), int | float)
    ]
    walltimes = [
        float(record.payload["walltime_s"])
        for record in records
        if isinstance(record.payload.get("walltime_s"), int | float)
    ]
    return CellEvidence(
        measured_seeds=len(records),
        mean=statistics.fmean(values) if values else 0.0,
        spread=statistics.stdev(values) if len(values) > 1 else 0.0,
        walltime_s=statistics.fmean(walltimes) if walltimes else 0.0,
        task_id=records[0].schedule.task_id if records else "",
    )


def run_spread(records: Sequence[Record], metric: str) -> float:
    """The run's typical within-cell spread for a metric.

    The spread a cell shows is what tells a reader whether a difference is
    material, so the material effect a quest asks for is stated in the run's
    own units rather than in a dimensionless number nobody can check.
    """
    by_cell: dict[tuple[str, ...], list[float]] = {}
    for record in records:
        value = record.payload.get(metric)
        if not isinstance(value, int | float):
            continue
        key = tuple(getattr(record, axis.value, "") for axis in StructuralAxis)
        by_cell.setdefault(key, []).append(float(value))
    spreads = [
        statistics.stdev(values) for values in by_cell.values() if len(values) > 1
    ]
    return statistics.fmean(spreads) if spreads else 0.0


def replication_spec(
    source: RunSpec,
    target: CellTarget,
    *,
    plan: int,
    budget_seconds: float | None = None,
) -> RunSpec:
    """The run's own declaration, narrowed to one cell and grown to its seeds.

    The seed plan grows rather than shifts: the run keeps the seeds it has
    already measured, and the pipeline skips the identities the store already
    holds, seed by seed. A replication therefore measures the seeds the cell
    still owes, and nothing else.
    """
    data = source.to_dict()
    data["axes"] = [selection.model_dump(mode="json") for selection in target.axes()]
    data["n_seeds"] = plan
    if budget_seconds is not None:
        data["budget_seconds"] = budget_seconds
    return RunSpec.model_validate(data)


def replication_budget(per_seed_seconds: float, measurements: int) -> float:
    """The budget the missing measurements need."""
    return max(1.0, per_seed_seconds * measurements * BUDGET_HEADROOM)


def claim_sentence(
    target: CellTarget,
    *,
    metric: str,
    task: str,
    chance: float,
    threshold: float,
    min_seeds: int,
    kind: str,
) -> str:
    """The sentence a registration states.

    The threshold is a difference from the control, which for one cell is the
    chance level; the sentence says the absolute target as well, so a reader
    never has to reconstruct it.
    """
    cell = target.describe()
    target_accuracy = chance + threshold
    if kind == KIND_QUEST:
        return (
            f"On {task}, the cell {cell} reaches {target_accuracy:.3f} {metric} "
            f"(chance {chance:.3f} plus {threshold:.3f}) over {min_seeds} seeds, "
            f"before any measurement of it."
        )
    return (
        f"On {task}, the cell {cell} reproduces {target_accuracy:.3f} {metric} "
        f"(chance {chance:.3f} plus {threshold:.3f}) over {min_seeds} seeds, "
        f"confirming the effect measured in run {target.run_id}."
    )


def registration_payload(
    target: CellTarget,
    *,
    claim: str,
    metric: str,
    threshold: float,
    alpha: float,
    min_seeds: int,
    kind: str,
    created: str | None = None,
) -> dict[str, Any]:
    """A registration's contents.

    The six contract fields come from the system's own
    :class:`ThresholdRegistration`; the rest says which cell the registration
    is about, so a file on disk is readable without the dashboard that wrote
    it. ``registered_at`` is the moment the registration was written, which is
    what decides whether it can confirm a run: a threshold written after a run
    started was written with that run's data in hand.
    """
    registration = ThresholdRegistration(
        claim=claim,
        metric=metric,
        threshold=threshold,
        alpha=alpha,
        min_seeds=min_seeds,
        created=created or date.today().isoformat(),
    )
    payload: dict[str, Any] = registration.to_dict()
    payload["registered_at"] = datetime.now().isoformat()
    payload["run_id"] = target.run_id
    payload["kind"] = kind
    payload["coordinate"] = dict(target.coordinate)
    return payload


def registration_name(target: CellTarget, kind: str) -> str:
    """The file name a registration is written under."""
    return f"{target.run_id}_{kind}_{target.slug()}"


def _identity(payload: Mapping[str, Any]) -> tuple[Any, ...]:
    """What makes two registrations the same registration."""
    return (
        payload.get("claim"),
        payload.get("metric"),
        payload.get("threshold"),
        payload.get("alpha"),
        payload.get("min_seeds"),
        payload.get("run_id"),
        payload.get("kind"),
        tuple(sorted((payload.get("coordinate") or {}).items())),
    )


def write_registration(
    directory: Path,
    payload: Mapping[str, Any],
    *,
    name: str,
) -> tuple[Path, bool]:
    """Write a registration into the registry.

    Returns the path and whether it was written. A registration already on
    disk with the same content is left alone; one with different content is
    refused — a registered threshold is not edited in place.
    """
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{name}.json"
    if path.exists():
        existing = json.loads(path.read_text(encoding="utf-8"))
        if _identity(existing) == _identity(payload):
            return path, False
        msg = f"{path} already holds a different registration"
        raise FileExistsError(msg)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return path, True


def default_metric() -> str:
    """The payload key a cell's claim is about when the run names none."""
    from computronium.experiment.schema.metrics import objective_metric

    return objective_metric(ACCURACY_OBJECTIVE)


__all__ = [
    "ACCURACY_OBJECTIVE",
    "BUDGET_HEADROOM",
    "KIND_CONFIRMATION",
    "KIND_QUEST",
    "ActionUnavailableError",
    "CellEvidence",
    "CellTarget",
    "cell_evidence",
    "claim_sentence",
    "default_metric",
    "records_for_cell",
    "registration_name",
    "registration_payload",
    "replication_budget",
    "replication_spec",
    "run_spread",
    "write_registration",
]
