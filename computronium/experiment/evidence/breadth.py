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
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import TYPE_CHECKING

from computronium.core.system_trainer.spec import error_blind_credit
from computronium.experiment.evidence.claims import DEFAULT_MIN_SEEDS
from computronium.experiment.kernel.search_space import (
    compiled_void_rules,
    void_refusal,
)
from computronium.experiment.schema.axis import AXES_REGISTRIES, StructuralAxis
from computronium.experiment.schema.coordinate import Coordinate

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable

    from computronium.experiment.registry.task_registry import PassBar
    from computronium.experiment.schema.record import Record

__all__ = ["BreadthGate", "CreditBreadth", "breadth_gate"]

type Refusal = Callable[[Coordinate, str], str | None]


@dataclass(frozen=True, slots=True)
class CreditBreadth:
    """One credit's qualifying families and measurements."""

    credit: str
    families: tuple[tuple[str, int], ...]
    keys: int
    green: bool


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

    Returns:
        One row per declared error-aware credit. ``green`` is true only when
        every row holds at least two families.
    """
    credits = _error_aware_credits()
    if not credits:
        msg = "no error-aware credits declared; seed the registries before the gate"
        raise RuntimeError(msg)
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
