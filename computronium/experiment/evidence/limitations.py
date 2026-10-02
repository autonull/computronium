"""Limitations a run can derive from its own records.

R85 names a Claim/Evidence/Limitation triple, and the third element had no
data model: ``limitation`` appeared nowhere under ``experiment/``. Prose is
not a limitation section, so every line here is a *count of records* under a
stated filter, plus the filter itself. A limitation that cannot be recomputed
from the store is not shipped — that is what :attr:`Limitation.evidence` is
for, and what ``tests/property/test_claim_report_lock.py`` checks.

Every function here is pure over the records it is handed, so a report can be
derived for one run, one fidelity, or one axis slice with the same code.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from itertools import chain
from typing import TYPE_CHECKING, Final

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping, Sequence

    from computronium.experiment.schema.record import Record

__all__ = [
    "Limitation",
    "LimitationKind",
    "derive_limitations",
    "replication_keys_of",
]


class LimitationKind(StrEnum):
    """The limitations a record stream can answer for.

    Each kind is a filter over records (or over the run's own declaration), so
    each is re-derivable by a reader with the same store.
    """

    BUDGET_EXHAUSTED = "budget_exhausted"
    GATES_SKIPPED = "gates_skipped"
    QUARANTINED = "quarantined_cells"
    FAILURES_BY_CAUSE = "failures_by_cause"
    CELLS_ABANDONED = "cells_abandoned"
    FIDELITY_NOT_REACHED = "fidelity_not_reached"
    UNMEASURED_OBJECTIVES = "unmeasured_objectives"
    NO_ELIGIBLE_CLAIM = "no_eligible_claim"


@dataclass(frozen=True, slots=True)
class Limitation:
    """One derived limitation line.

    Attributes:
        kind: Which limitation this is.
        detail: The human-readable line, naming the count.
        count: How many records (or declarations) the limitation covers.
        evidence: The filter that recomputes ``count`` from the store, so the
            line is queryable rather than asserted.
    """

    kind: LimitationKind
    detail: str
    count: int
    evidence: str

    def __post_init__(self) -> None:
        if self.count < 0:
            msg = f"Limitation.count must be non-negative, got {self.count}"
            raise ValueError(msg)
        if not self.evidence:
            msg = "Limitation.evidence must name the filter that derives it"
            raise ValueError(msg)


FIDELITY_ORDER: Final[Mapping[str, int]] = {"L0": 0, "L1": 1, "L2": 2}


def replication_keys_of(records: Sequence[Record]) -> tuple[str, ...]:
    """The distinct replication keys a record set measured, in stable order."""
    from computronium.experiment.evidence.claims import replication_key

    return tuple(sorted({replication_key(r) for r in records}))


@dataclass(frozen=True, slots=True)
class _Context:
    """What a limitation may be derived from: the records, and the declaration."""

    records: Sequence[Record]
    achieved: Mapping[str, int] | None = None
    n_seeds: int | None = None
    fidelity: str | None = None
    objectives: Sequence[str] = ()
    claim_count: int | None = None


def _quarantined(ctx: _Context) -> tuple[Limitation, ...]:
    records = [r for r in ctx.records if r.status.quarantine]
    if not records:
        return ()
    return (
        Limitation(
            kind=LimitationKind.QUARANTINED,
            detail=f"{len(records)} record(s) quarantined and excluded from claims",
            count=len(records),
            evidence="records WHERE status.quarantine",
        ),
    )


def _failures_by_cause(ctx: _Context) -> tuple[Limitation, ...]:
    counts: dict[str, int] = {}
    for record in ctx.records:
        cause = record.status.cause.value
        if cause != "unknown":
            counts[cause] = counts.get(cause, 0) + 1
    return tuple(
        Limitation(
            kind=LimitationKind.FAILURES_BY_CAUSE,
            detail=f"{count} record(s) failed with cause {cause}",
            count=count,
            evidence=f"records GROUP BY status.cause WHERE cause = {cause!r}",
        )
        for cause, count in sorted(counts.items())
    )


def _gates_skipped(ctx: _Context) -> tuple[Limitation, ...]:
    records = [
        r
        for r in ctx.records
        if r.status.gate_verdict.value in {"PENDING", "QUARANTINE"}
    ]
    if not records:
        return ()
    return (
        Limitation(
            kind=LimitationKind.GATES_SKIPPED,
            detail=f"{len(records)} record(s) never reached a PASS or FAIL gate verdict",
            count=len(records),
            evidence="records WHERE status.gate_verdict IN ('PENDING', 'QUARANTINE')",
        ),
    )


def _cells_abandoned(ctx: _Context) -> tuple[Limitation, ...]:
    if ctx.n_seeds is None or ctx.achieved is None:
        return ()
    keys = replication_keys_of(ctx.records)
    short = [key for key in keys if ctx.achieved.get(key, 0) < ctx.n_seeds]
    if not short:
        return ()
    return (
        Limitation(
            kind=LimitationKind.CELLS_ABANDONED,
            detail=(
                f"{len(short)} of {len(keys)} cell(s) reached fewer than the declared "
                f"{ctx.n_seeds} seeds"
            ),
            count=len(short),
            evidence="count_achieved_seeds(replication_key) < spec.n_seeds, per cell",
        ),
    )


def _fidelity_not_reached(ctx: _Context) -> tuple[Limitation, ...]:
    if ctx.fidelity is None:
        return ()
    target = FIDELITY_ORDER.get(ctx.fidelity, 0)
    reached = any(
        FIDELITY_ORDER.get(r.schedule.fidelity, 0) >= target for r in ctx.records
    )
    if reached:
        return ()
    seen = sorted({r.schedule.fidelity for r in ctx.records})
    return (
        Limitation(
            kind=LimitationKind.FIDELITY_NOT_REACHED,
            detail=(
                f"declared fidelity {ctx.fidelity} was never reached; records exist at "
                f"{seen or ['none']}"
            ),
            count=len(ctx.records),
            evidence=f"records WHERE schedule.fidelity != {ctx.fidelity!r}",
        ),
    )


def _unmeasured_objectives(ctx: _Context) -> tuple[Limitation, ...]:
    from computronium.experiment.schema.metrics import measured_objectives

    unmeasured = [
        name for name in ctx.objectives if name not in set(measured_objectives())
    ]
    if not unmeasured:
        return ()
    return (
        Limitation(
            kind=LimitationKind.UNMEASURED_OBJECTIVES,
            detail=(
                f"{len(unmeasured)} declared objective(s) no measurement satisfies: "
                f"{', '.join(unmeasured)}"
            ),
            count=len(unmeasured),
            evidence="RunSpec.objectives - measured_objectives()",
        ),
    )


def _no_eligible_claim(ctx: _Context) -> tuple[Limitation, ...]:
    if ctx.claim_count is None or ctx.claim_count > 0:
        return ()
    return (
        Limitation(
            kind=LimitationKind.NO_ELIGIBLE_CLAIM,
            detail="no record met the claim eligibility predicates, so no claim is made",
            count=0,
            evidence="claims.derive_claims(...) filtered by claim eligibility",
        ),
    )


# The limitations a run reports, in report order. Adding one is a row here.
_DERIVATIONS: Final[tuple[Callable[[_Context], tuple[Limitation, ...]], ...]] = (
    _quarantined,
    _failures_by_cause,
    _gates_skipped,
    _cells_abandoned,
    _fidelity_not_reached,
    _unmeasured_objectives,
    _no_eligible_claim,
)


def derive_limitations(
    records: Sequence[Record],
    *,
    achieved: Mapping[str, int] | None = None,
    n_seeds: int | None = None,
    fidelity: str | None = None,
    objectives: Sequence[str] = (),
    claim_count: int | None = None,
) -> tuple[Limitation, ...]:
    """Derive a run's limitations from its records and its own declaration.

    Args:
        records: The run's records (or any slice of them).
        achieved: Achieved PASS seeds per replication key, as
            ``RecordStore.count_achieved_seeds`` reports them.
        n_seeds: Seeds the spec declared, for the abandoned-cell check.
        fidelity: Fidelity the spec declared, for the not-reached check.
        objectives: Objective names the spec declared, for the unmeasured check.
        claim_count: How many claims the run could make; ``None`` when not
            derived, which suppresses that limitation rather than guessing.

    Returns:
        Limitations in a fixed order, one per kind that applies.
    """
    ctx = _Context(
        records=records,
        achieved=achieved,
        n_seeds=n_seeds,
        fidelity=fidelity,
        objectives=objectives,
        claim_count=claim_count,
    )
    return tuple(chain.from_iterable(derive(ctx) for derive in _DERIVATIONS))
