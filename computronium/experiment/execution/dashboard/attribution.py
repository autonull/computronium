"""What the run can attribute, and what it cannot (TODO69).

An attribution needs a design that varied more than one thing. This reads
the run's arms — the same statistics the ledger draws — and says which
axes moved the objective, how far apart their arms stand, and whether the
run is big enough to say which of them mattered most.

The forest in ``axis_attribution`` is not run here, and that is a
decision rather than an omission. Twenty records over one varied axis
give a random forest over one-hot features nothing to fit, and what it
returns would be a worse attribution than the spread the ledger already
draws. The view says plainly that the design is too small to attribute,
which is both the honest answer and the more useful one: a reader who
knows which axes were held fixed cannot be misled by a number.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from computronium.experiment.execution.dashboard.arms import axis_arms

if TYPE_CHECKING:
    from computronium.experiment.evidence.store import RecordStore

# How many axes must vary before a run can say which of them mattered.
MIN_VARIED_AXES = 2


def _reason(varied: list[str], held: list[str]) -> str:
    """Why the run can or cannot attribute, in one sentence."""
    if not varied:
        return (
            "Nothing varied: the run measured one configuration, "
            "so there is nothing to attribute."
        )
    if len(varied) == 1:
        return (
            f"One axis varied ({varied[0]}) and {len(held)} were held fixed: "
            f"this run can speak about {varied[0]} alone."
        )
    return (
        f"{len(varied)} axes varied ({', '.join(varied)}): the run can say "
        f"which of them moved the objective."
    )


def _summary(varied: list[str], held: list[str], records: int) -> str:
    """The run's design, in one line: what it varied, and what it pinned."""
    parts = [f"{records} records"]
    if varied:
        parts.append(f"{len(varied)} axis varied: {', '.join(varied)}")
    else:
        parts.append("no axis varied")
    if held:
        parts.append(f"{len(held)} held fixed: {', '.join(held)}")
    return " · ".join(parts)


def attribution_payload(store: RecordStore, run_id: str) -> dict[str, Any]:
    """What the run can attribute, and what its design cannot say.

    Args:
        store: The store the run wrote to.
        run_id: The run the attribution is about.

    Returns:
        The payload the browser draws: every axis, whether it varied, how far
        apart its arms stand, and the arms themselves; and the plain reason
        the run can or cannot say which axis mattered.
    """
    from computronium.experiment.surface.report import ReportGenerator

    generator = ReportGenerator(store)
    records = list(store.query_records(run_id=run_id))
    metrics = generator.claim_metrics(run_id)
    metric = metrics[0] if metrics else ""
    if not metric:
        return {"run_id": run_id, "metric": "", "records": len(records), "axes": []}

    axes = axis_arms(records, metric)
    varied = [arms.axis for arms in axes if arms.varied]
    held = [arms.axis for arms in axes if not arms.varied]

    return {
        "run_id": run_id,
        "metric": metric,
        "records": len(records),
        "axes": [
            {
                "axis": arms.axis,
                "varied": arms.varied,
                "spread": arms.spread,
                "values": [
                    {
                        "value": arm.value,
                        "mean": arm.mean,
                        "sd": arm.sd,
                        "n": arm.n,
                        "cells": arm.cells,
                        "verdict": arm.verdict,
                    }
                    for arm in arms.values
                ],
            }
            for arms in axes
        ],
        "varied_axes": varied,
        "held_axes": held,
        "attributable": len(varied) >= MIN_VARIED_AXES,
        "reason": _reason(varied, held),
        "summary": _summary(varied, held, len(records)),
    }


__all__ = ["MIN_VARIED_AXES", "attribution_payload"]
