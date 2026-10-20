"""What the run can say, and what it can show for itself (TODO69).

The stage draws the run twice over: as a *ledger* — every arm it measured,
the evidence behind it and the gate's standing on it — and as a *contrast* —
its arms against one another, with the test it could or could not run.

The rules live here, on the server. The browser draws what it is given: a
claim, a verdict or a floor the browser worked out for itself would be a
second truth about the same run, and a dashboard with two truths about a run
is a dashboard that cannot be believed.

The contrast is measured on the run's *own objective* — the first metric its
declaration claims — and on the axis whose values spread widest on it. The
report's own significance test is quoted in the ledger: it is the report's
account, and the report chooses its own metric.
"""

from __future__ import annotations

import math
import statistics
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from computronium.experiment.evidence.claims import Claim
    from computronium.experiment.evidence.store import RecordStore
    from computronium.experiment.schema.record import Record


def _number(value: float | None) -> float | None:
    """A number the browser can hold: JSON has no NaN, and no infinity."""
    if value is None:
        return None
    if isinstance(value, float) and not math.isfinite(value):
        return None
    return float(value)


def _metric_values(records: list[Record], metric: str) -> list[float]:
    """The records' values of one metric, and only the ones that carry it."""
    values: list[float] = []
    for record in records:
        value = record.payload.get(metric)
        if isinstance(value, bool) or not isinstance(value, int | float):
            continue
        values.append(float(value))
    return values


def _arm_rows(
    records: list[Record],
    metric: str,
    min_seeds: int,
) -> list[dict[str, Any]]:
    """Every arm the run measured, with its evidence and the gate's standing.

    An arm is one value of one axis. Its standing is the gate's verdict
    read the way the claim rules read it: a cell that never reached the
    seed floor cannot back a claim, and a cell the gate refused cannot back
    one either. The arms that fall short are here, because a ledger that
    lists only the claims is a ledger that hides the holes.
    """
    from computronium.experiment.evidence.claims import replication_key
    from computronium.experiment.execution.statistical_promotion import (
        StatisticalVerdict,
    )
    from computronium.experiment.schema.axis import StructuralAxis

    rows: list[dict[str, Any]] = []
    for axis in StructuralAxis:
        arms: dict[str, list[Record]] = {}
        for record in records:
            arms.setdefault(getattr(record, axis.value), []).append(record)
        if len(arms) < 2:
            continue

        for value, arm in arms.items():
            cells: dict[str, list[Record]] = {}
            for record in arm:
                cells.setdefault(replication_key(record), []).append(record)
            passed = max(
                (
                    sum(
                        1
                        for record in cell
                        if record.status.gate_verdict.value == "PASS"
                    )
                    for cell in cells.values()
                ),
                default=0,
            )
            if passed == 0:
                verdict = StatisticalVerdict.REJECTED
            elif passed < min_seeds:
                verdict = StatisticalVerdict.INSUFFICIENT
            else:
                verdict = StatisticalVerdict.PASSED

            values = _metric_values(arm, metric)
            rows.append({
                "axis": axis.value,
                "value": value,
                "mean": statistics.fmean(values) if values else 0.0,
                "sd": statistics.stdev(values) if len(values) > 1 else 0.0,
                "n": len(values),
                "cells": len(cells),
                "verdict": verdict.value,
            })
    return rows


def _fixed_rows(records: list[Record], metric: str) -> list[dict[str, Any]]:
    """The axes that did not vary: one value each, and the whole run behind it."""
    from computronium.experiment.evidence.claims import replication_key
    from computronium.experiment.schema.axis import StructuralAxis

    rows: list[dict[str, Any]] = []
    for axis in StructuralAxis:
        values = {getattr(record, axis.value) for record in records}
        if len(values) != 1:
            continue
        value = next(iter(values))
        cells = {replication_key(record) for record in records}
        measured = _metric_values(records, metric)
        rows.append({
            "axis": axis.value,
            "value": value,
            "mean": statistics.fmean(measured) if measured else 0.0,
            "n": len(measured),
            "cells": len(cells),
        })
    return rows


def ledger_payload(store: RecordStore, run_id: str) -> dict[str, Any]:
    """The run's account of what it can say.

    Args:
        store: The store the run wrote to.
        run_id: The run the ledger is about.

    Returns:
        The payload the browser draws: every arm the run measured, its
        evidence and the gate's standing on it; the axes that did not vary;
        the limitations the report derived; and the report's own significance
        line.
    """
    from computronium.experiment.evidence.claims import DEFAULT_MIN_SEEDS
    from computronium.experiment.surface.report import (
        ReportGenerator,
        chance_level,
    )

    generator = ReportGenerator(store)
    records = list(store.query_records(run_id=run_id))
    metrics = generator.claim_metrics(run_id)
    metric = metrics[0] if metrics else ""

    claims: tuple[Claim, ...] = generator.claims(run_id)
    by_arm = {(claim.metric, claim.axis, claim.value): claim for claim in claims}

    rows = _arm_rows(records, metric, DEFAULT_MIN_SEEDS)
    for row in rows:
        claim = by_arm.get((metric, row["axis"], row["value"]))
        if claim is None:
            continue
        # The report's own numbers win where the report has them: the
        # ledger quotes the claim rather than recomputing it.
        row["mean"] = claim.mean
        row["sd"] = math.sqrt(claim.variance)
        row["n"] = claim.n
        row["cells"] = claim.cells
    rows.sort(key=lambda row: (row["axis"], -row["mean"], row["value"]))

    info = store.query_run(run_id)
    task = (
        info.spec.task_names[0] if info and info.spec and info.spec.task_names else None
    )
    significance = generator.significance(run_id)

    return {
        "run_id": run_id,
        "metric": metric,
        "claims": rows,
        "fixed": _fixed_rows(records, metric),
        "standings": _standing_counts(rows),
        "limitations": [
            {
                "kind": limitation.kind.value,
                "detail": limitation.detail,
                "count": limitation.count,
            }
            for limitation in generator.limitations(run_id)
        ],
        "significance": significance.render() if significance else "",
        "min_seeds": DEFAULT_MIN_SEEDS,
        "chance": chance_level(task, metric) if metric else None,
    }


def _standing_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    """How many arms stand each way: the ledger's headline."""
    counts: dict[str, int] = {}
    for row in rows:
        verdict = str(row["verdict"])
        counts[verdict] = counts.get(verdict, 0) + 1
    return counts


def _pair_rows(
    by_value: dict[str, dict[str, Any]],
    leader: Claim,
    others: list[Claim],
) -> list[dict[str, Any]]:
    """The leader against every other arm, over the cells they share.

    The difference is the paired one: the mean of the per-cell differences
    over the cells both arms measured, which is what a paired test measures
    and what a difference of means is not.
    """
    pairs: list[dict[str, Any]] = []
    for other in others:
        shared = sorted(
            set(by_value.get(leader.value, {})) & set(by_value.get(other.value, {}))
        )
        difference = None
        if shared:
            difference = sum(
                by_value[leader.value][key].mean - by_value[other.value][key].mean
                for key in shared
            ) / len(shared)
        pairs.append({
            "a": leader.value,
            "b": other.value,
            "difference": _number(difference),
            "shared_cells": len(shared),
        })
    return pairs


def contrast_payload(store: RecordStore, run_id: str) -> dict[str, Any]:
    """The run's arms against one another, and the test it could not run.

    The arms are the values of the axis that spread widest on the run's own
    objective. Each pair is measured over the cells the two arms share, which
    is what a paired test needs — and what it lacked, when the run did not
    have enough of them.

    Args:
        store: The store the run wrote to.
        run_id: The run the contrast is about.

    Returns:
        The payload the browser draws: the arms, the pairs between them, and
        the test's verdict with the coverage that decided it.
    """
    from computronium.experiment.evidence.claims import (
        DEFAULT_MIN_SEEDS,
        cell_metrics_by_axis_value,
    )
    from computronium.experiment.evidence.significance import (
        MIN_SHARED_CELLS,
        Resampling,
        paired_significance,
    )
    from computronium.experiment.schema.axis import StructuralAxis
    from computronium.experiment.surface.report import ReportGenerator

    generator = ReportGenerator(store)
    claims = generator.claims(run_id)
    metrics = generator.claim_metrics(run_id)
    metric = metrics[0] if metrics else ""
    if not metric:
        return {}

    by_axis: dict[str, list[Claim]] = {}
    for claim in claims:
        if claim.metric == metric:
            by_axis.setdefault(claim.axis, []).append(claim)

    spreads = {
        axis: max(c.mean for c in rows) - min(c.mean for c in rows)
        for axis, rows in by_axis.items()
        if len(rows) > 1
    }
    if not spreads:
        return {}
    axis = max(spreads, key=lambda name: (spreads[name], name))

    arms = sorted(by_axis[axis], key=lambda c: (-c.mean, c.value))
    leader = arms[0]
    lowest = arms[-1]

    records = list(store.query_records(run_id=run_id))
    achieved = generator.achieved_seeds(run_id)
    by_value = cell_metrics_by_axis_value(
        records,
        axis=StructuralAxis(axis),
        metric=metric,
        achieved=achieved,
        min_seeds=DEFAULT_MIN_SEEDS,
    )

    pairs = _pair_rows(by_value, leader, arms[1:])

    test = paired_significance(
        by_value.get(leader.value, {}),
        by_value.get(lowest.value, {}),
        axis=axis,
        metric=metric,
        best_value=leader.value,
        worst_value=lowest.value,
        resampling=Resampling(),
    )

    return {
        "run_id": run_id,
        "axis": axis,
        "metric": metric,
        "arms": [
            {
                "value": arm.value,
                "mean": arm.mean,
                "sd": math.sqrt(arm.variance),
                "n": arm.n,
                "cells": arm.cells,
            }
            for arm in arms
        ],
        "pairs": pairs,
        "test": {
            "tested": test.tested,
            "significant": test.significant,
            "p_value": _number(test.p_value),
            "ci_lower": _number(test.ci_lower),
            "ci_upper": _number(test.ci_upper),
            "cohens_dz": _number(test.cohens_dz),
            "mean_diff": _number(test.mean_diff),
            "shared_cells": test.shared_cells,
            "required_cells": MIN_SHARED_CELLS,
            "alpha": test.alpha,
        },
    }


__all__ = ["contrast_payload", "ledger_payload"]
