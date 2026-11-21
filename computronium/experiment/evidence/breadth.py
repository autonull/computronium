"""The AGENTS breadth exit as a predicate, not a sentence.

AGENTS.md's breadth exit is: every error-aware credit holds a legal,
above-chance **L2/n>=5** cell on **>=2 task families**. This module is the one
implementation of that sentence; ``comp gate breadth`` prints it and exits
non-zero while any credit falls short.

A family is the task's registered domain (``TaskSpecEnriched.domain``), not its
task id. That is the coarser reading on purpose: two tasks in one domain count
once, so the gate cannot be passed by renaming a sibling task.

"Above chance" is the record's own ``pass_bar_cleared`` when it carries one;
a legacy record (written before the gate bar) is re-assessed against its task's
declared ruler (``primary_pass_bar``) instead of being dropped. The bar is the
single source; the flag is its cached derivation. "Legal" is the declared void
rules for the record's own task (``compiled_void_rules``); a measured cell on a
refused combination cannot count, even if it predates the rule.

``BREADTH_GAPS`` is the check's own gap table: a credit that cannot hold a
second family because the repository declares none is accounted by a named
reason and the row that opens it. A gap never turns the exit green; it makes
the red output actionable, and an unaccounted credit is the defect.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from types import MappingProxyType
from typing import TYPE_CHECKING, Final

from computronium.core.system_trainer.spec import error_blind_credit
from computronium.experiment.evidence.claims import DEFAULT_MIN_SEEDS
from computronium.experiment.kernel.search_space import (
    compiled_void_rules,
    void_refusal,
)
from computronium.experiment.schema.axis import AXES_REGISTRIES, StructuralAxis
from computronium.experiment.schema.coordinate import Coordinate

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable, Mapping

    from computronium.experiment.registry.task_registry import PassBar
    from computronium.experiment.schema.record import Record

__all__ = [
    "BREADTH_GAPS",
    "BreadthGap",
    "BreadthGate",
    "CreditBreadth",
    "breadth_gate",
]

type Refusal = Callable[[Coordinate, str], str | None]


@dataclass(frozen=True, slots=True)
class BreadthGap:
    """Why a credit cannot hold a second family, and the row that opens it.

    ``family`` is the domain the closing row would add; ``cost_s`` is the
    measured price of the five-seed row at that family's base box.
    """

    reason: str
    trigger: str
    family: str
    cost_s: float


#: The one reason the three time-major credits cannot hold a second family:
#: every declared task loads a flat batch, and their rl half is refused by the
#: error-aware rule. The closing row is a declared time-major task; its price is
#: the five-seed row at char_ngram's 10-epoch base (37 s/seed measured).
_TIME_MAJOR_GAP: Final[BreadthGap] = BreadthGap(
    reason=(
        "declares sequence + rl: char_ngram and copy_task load flat batches, "
        "so the time-major sequence half has no legal cell; "
        "rl_credit_must_be_error_blind refuses the rl half because the credit "
        "reads error"
    ),
    trigger=(
        "a declared time-major task (batch_layout=time_major, loader yields "
        "(time, batch, features)), or a measured reason to retire the credit"
    ),
    family="sequence",
    cost_s=185.0,
)


#: The check's own gaps, keyed by credit name. Every error-aware credit the
#: gate fails must name one; the three time-major credits are the whole table.
BREADTH_GAPS: Final[Mapping[str, BreadthGap]] = MappingProxyType(
    dict.fromkeys(
        ("eligibility_prop", "rtrl_reference", "unbiased_rtrl"), _TIME_MAJOR_GAP
    )
)


@dataclass(frozen=True, slots=True)
class CreditBreadth:
    """One credit's qualifying families and measurements, plus its gap."""

    credit: str
    families: tuple[tuple[str, int], ...]
    keys: int
    green: bool
    gap: BreadthGap | None = None

    @property
    def accounted(self) -> bool:
        """Whether the row is measured on two families or parked by a gap."""
        return self.green or self.gap is not None


@dataclass(frozen=True, slots=True)
class BreadthGate:
    """The whole gate: every error-aware credit, plus its exclusions."""

    credits: tuple[CreditBreadth, ...]
    assessed_legacy: int
    excluded_unbarred: int
    excluded_refused: int

    @property
    def green(self) -> bool:
        """Whether every declared error-aware credit holds two families."""
        return all(row.green for row in self.credits)

    @property
    def unaccounted(self) -> tuple[str, ...]:
        """The credits below two families and outside the gap table."""
        return tuple(row.credit for row in self.credits if not row.accounted)

    @property
    def gaps(self) -> tuple[CreditBreadth, ...]:
        """The rows a declared gap parks, in credit order."""
        return tuple(row for row in self.credits if row.gap is not None)


def _error_aware_credits() -> tuple[str, ...]:
    declared = AXES_REGISTRIES[StructuralAxis.CREDIT].keys()
    return tuple(sorted(name for name in declared if not error_blind_credit(name)))


def _clears_bar(record: Record, bar: PassBar) -> bool:
    """Re-assess a legacy record against its task's declared ruler."""
    flag = record.payload.get("pass_bar_cleared")
    if flag is not None:
        return flag is True
    metric = record.payload.get(bar.metric_key)
    if not isinstance(metric, int | float) or not math.isfinite(metric):
        return False
    return metric > bar.value if bar.direction == "maximize" else metric < bar.value


def _record_state(record: Record, bar: PassBar | None) -> str:
    """Classify one record: ``qualify``, ``unbarred``, or ``skip``."""
    if record.status.gate_verdict.value != "PASS":
        return "skip"
    if record.schedule.fidelity != "L2":
        return "skip"
    if record.schedule.n_seeds < DEFAULT_MIN_SEEDS:
        return "skip"
    if bar is None or not _clears_bar(record, bar):
        return "unbarred"
    return "qualify"


def breadth_gate(
    records: Iterable[Record],
    family_of: Callable[[str], str],
    bar_of: Callable[[str], PassBar | None],
    *,
    refusal: Refusal | None = None,
    gaps: Mapping[str, BreadthGap] | None = None,
) -> BreadthGate:
    """Evaluate AGENTS' breadth exit over a record stream.

    Args:
        records: Every record the corpus holds. Duplicates across stores are
            deduplicated by ``measurement_key``.
        family_of: Maps a task id to its family (registered domain).
        bar_of: Maps a task id to its declared ruler, or ``None`` when the
            task derives none.
        refusal: Optional legality predicate; defaults to the declared void
            rules. A non-``None`` return means the cell is refused.
        gaps: Optional capability-gap table; defaults to ``BREADTH_GAPS``.
            A gap parks a credit below two families; it never makes it green.

    Returns:
        One row per declared error-aware credit. ``green`` is true only when
        every row holds at least two families; ``unaccounted`` names the rows
        that are neither green nor parked by a declared gap.
    """
    credits = _error_aware_credits()
    if not credits:
        msg = "no error-aware credits declared; seed the registries before the gate"
        raise RuntimeError(msg)
    declared_gaps = BREADTH_GAPS if gaps is None else gaps
    check = refusal if refusal is not None else _declared_refusal()
    families: dict[str, dict[str, set[str]]] = {credit: {} for credit in credits}
    assessed_legacy = 0
    excluded_unbarred = 0
    excluded_refused = 0

    for record in records:
        if record.credit not in families:
            continue
        task = record.schedule.task_id
        state = _record_state(record, bar_of(task))
        if state == "skip":
            continue
        if state == "unbarred":
            excluded_unbarred += 1
            continue
        if record.payload.get("pass_bar_cleared") is None:
            assessed_legacy += 1
        coordinate = Coordinate.from_record(record)
        if check(coordinate, task) is not None:
            excluded_refused += 1
            continue
        family = family_of(task)
        families[record.credit].setdefault(family, set()).add(record.measurement_key)

    rows = tuple(
        CreditBreadth(
            credit=credit,
            families=tuple(
                (family, len(keys)) for family, keys in sorted(measured.items())
            ),
            keys=sum(len(keys) for keys in measured.values()),
            green=len(measured) >= 2,
            gap=None if len(measured) >= 2 else declared_gaps.get(credit),
        )
        for credit, measured in sorted(families.items())
    )
    return BreadthGate(
        credits=rows,
        assessed_legacy=assessed_legacy,
        excluded_unbarred=excluded_unbarred,
        excluded_refused=excluded_refused,
    )


def _declared_refusal() -> Refusal:
    rules = compiled_void_rules()

    def check(coordinate: Coordinate, task: str) -> str | None:
        return void_refusal(rules, coordinate, task)

    return check
