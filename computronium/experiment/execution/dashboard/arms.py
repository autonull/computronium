"""The run's arms: what each value of an axis measured (TODO69).

An arm is one value of one axis — the gradient credit rule, the recurrent
geometry — and the statistics of an arm are the same wherever they are
wanted. The ledger lists them with the gate's standing on them; the
attribution asks how far apart they stand. Both read this module, so the
two pictures cannot disagree about what an arm measured.

The statistics are read over every record of the arm, not only the ones
that could back a claim: an arm that fell short of the seed floor still
measured something, and a picture that hides it hides the hole the run
leaves behind.
"""

from __future__ import annotations

import statistics
from dataclasses import dataclass
from typing import TYPE_CHECKING

from computronium.experiment.evidence.claims import DEFAULT_MIN_SEEDS

if TYPE_CHECKING:
    from collections.abc import Sequence

    from computronium.experiment.schema.record import Record


@dataclass(frozen=True, slots=True)
class ArmStats:
    """One arm's evidence: what it measured, and how much of it there is."""

    value: str
    mean: float
    sd: float
    n: int
    cells: int
    verdict: str


@dataclass(frozen=True, slots=True)
class AxisArms:
    """Every arm of one axis, and whether the axis varied at all."""

    axis: str
    values: tuple[ArmStats, ...]

    @property
    def varied(self) -> bool:
        """Whether the axis took more than one value in this run."""
        return len(self.values) > 1

    @property
    def spread(self) -> float:
        """How far apart the arms stand: the best arm minus the worst."""
        if not self.values:
            return 0.0
        means = [arm.mean for arm in self.values]
        return max(means) - min(means)


def metric_values(records: Sequence[Record], metric: str) -> list[float]:
    """The records' values of one metric, and only the ones that carry it."""
    values: list[float] = []
    for record in records:
        value = record.payload.get(metric)
        if isinstance(value, bool) or not isinstance(value, int | float):
            continue
        values.append(float(value))
    return values


def arm_standing(records: Sequence[Record], min_seeds: int) -> str:
    """The gate's standing on one arm.

    An arm is measured cell by cell, and a cell backs a claim only if enough
    of its seeds passed the gate. The arm stands as its best cell: one cell
    that reached the floor is enough for the arm to stand, and an arm with no
    passing cell at all is rejected rather than merely short of seeds.
    """
    from computronium.experiment.evidence.claims import replication_key
    from computronium.experiment.execution.statistical_promotion import (
        StatisticalVerdict,
    )

    cells: dict[str, list[Record]] = {}
    for record in records:
        cells.setdefault(replication_key(record), []).append(record)
    passed = max(
        (
            sum(1 for record in cell if record.status.gate_verdict.value == "PASS")
            for cell in cells.values()
        ),
        default=0,
    )
    if passed == 0:
        return StatisticalVerdict.REJECTED.value
    if passed < min_seeds:
        return StatisticalVerdict.INSUFFICIENT.value
    return StatisticalVerdict.PASSED.value


def axis_arms(
    records: Sequence[Record],
    metric: str,
    min_seeds: int = DEFAULT_MIN_SEEDS,
) -> tuple[AxisArms, ...]:
    """The arms of every axis, from the records the run wrote.

    Args:
        records: The run's records.
        metric: The payload key to summarise.
        min_seeds: The seeds a cell must have passed the gate with.

    Returns:
        One entry per axis, in the order the ontology declares them, with an
        arm for every value the run measured on it. An axis the run held at
        one value has a single arm, and says so.
    """
    from computronium.experiment.evidence.claims import replication_key
    from computronium.experiment.schema.axis import StructuralAxis

    axes: list[AxisArms] = []
    for axis in StructuralAxis:
        by_value: dict[str, list[Record]] = {}
        for record in records:
            by_value.setdefault(getattr(record, axis.value, ""), []).append(record)

        values: list[ArmStats] = []
        for value, group in by_value.items():
            if not value:
                continue
            measured = metric_values(group, metric)
            values.append(
                ArmStats(
                    value=value,
                    mean=statistics.fmean(measured) if measured else 0.0,
                    sd=statistics.stdev(measured) if len(measured) > 1 else 0.0,
                    n=len(measured),
                    cells=len({replication_key(record) for record in group}),
                    verdict=arm_standing(group, min_seeds),
                )
            )
        values.sort(key=lambda arm: (-arm.mean, arm.value))
        axes.append(AxisArms(axis=axis.value, values=tuple(values)))
    return tuple(axes)


__all__ = ["ArmStats", "AxisArms", "axis_arms", "metric_values"]
