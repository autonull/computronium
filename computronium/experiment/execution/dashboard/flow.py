"""The run's cells, from the space to the evidence (TODO69).

A run is a process before it is an evidence, and the process is in the
events: the stages the run reached, the counts each stage reported, the
cells the gate refused, and the measurements that became records. This
lays them out as a flow — what the run held, what it threw away, and
what it wrote down — so a reader can see the shape of the run rather
than only its results.

The events are the ones this dashboard watched. A run that happened in
another process has no flow here, and the picture says so rather than
inventing one.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from computronium.experiment.execution.events import STAGE_ACTIONS

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

# What a stage's count is: the cells it carried, or the records it wrote.
KIND_CELLS = "cells"
KIND_RECORDS = "records"
KIND_NONE = "none"

# The numbers a sentence says in words.
_WORDS = (
    "no",
    "one",
    "two",
    "three",
    "four",
    "five",
    "six",
    "seven",
    "eight",
    "nine",
    "ten",
    "eleven",
    "twelve",
    "thirteen",
    "fourteen",
    "fifteen",
    "sixteen",
    "seventeen",
    "eighteen",
    "nineteen",
    "twenty",
)


def _words(count: int) -> str:
    """A count said in words, when there is a word for it."""
    if 0 <= count < len(_WORDS):
        return _WORDS[count]
    return str(count)


@dataclass(frozen=True, slots=True)
class StageFlow:
    """One stage of the run, and what it handled."""

    stage: str
    action: str
    count: int
    kind: str
    refused: int
    events: int
    cells: tuple[str, ...]


def _stage_flow(stage: str, frames: Sequence[Mapping[str, Any]]) -> StageFlow:
    """What one stage did, from the events it left.

    Three kinds of event come out of a stage. The announcement says what the
    stage produced, in one number per kind; the records it wrote arrive one
    batch at a time; and the measurements arrive one cell at a time, each
    naming the cell it measured.

    The cells are the *peak* — the most the stage held at once, because a
    stage that ran a second round held the same cells again. The records are
    the *total* — a record is a measurement, and the batches of them add up.
    """
    proposals = 0
    announced = 0
    batched = 0
    measurements = 0
    refused = 0
    cells: list[str] = []

    for frame in frames:
        detail = frame.get("detail")
        detail = detail if isinstance(detail, dict) else {}
        if "proposals" in detail and "records" in detail:
            proposals = max(proposals, _count(detail.get("proposals")))
            announced = max(announced, _count(detail.get("records")))
        elif "records" in detail:
            batched += _count(detail.get("records"))
        if "cell" in detail:
            measurements += 1
            cells.append(str(detail.get("cell") or ""))
        refused = max(refused, _count(detail.get("refused")))

    records = max(announced, batched, measurements)
    if proposals:
        count, kind = proposals, KIND_CELLS
    elif records:
        count, kind = records, KIND_RECORDS
    else:
        count, kind = 0, KIND_NONE

    return StageFlow(
        stage=stage,
        action=STAGE_ACTIONS.get(stage, stage),
        count=count,
        kind=kind,
        refused=refused,
        events=len(frames),
        cells=tuple(dict.fromkeys(cells)),
    )


def _count(value: object) -> int:
    """A count the events reported, as a whole number."""
    if isinstance(value, bool) or not isinstance(value, int | float):
        return 0
    return int(value)


def _summary(stages: Sequence[StageFlow], measured: int, records: int) -> str:
    """The run's shape, in one sentence."""
    if not stages:
        return "This dashboard did not watch this run: it has no stages of its own."
    held = max((stage.count for stage in stages if stage.kind == KIND_CELLS), default=0)
    refusals = sum(stage.refused for stage in stages)
    clauses = [
        f"{_words(held)} cell{'s' if held != 1 else ''} went through the pipeline"
    ]
    clauses.append(
        f"the gate refused {_words(refusals)}" if refusals else "the gate refused none"
    )
    if measured:
        clauses.append(
            f"{_words(measured)} cell{'s' if measured != 1 else ''} measured"
        )
    if records:
        clauses.append(f"{_words(records)} record{'s' if records != 1 else ''} written")
    return "; ".join(clauses) + "."


def flow_payload(
    events: Sequence[Mapping[str, Any]],
    run_id: str | None = None,
) -> dict[str, Any]:
    """The run's cells, from the space to the evidence.

    Args:
        events: The run's event frames, in the order they arrived.
        run_id: The run the flow is about.

    Returns:
        The payload the browser draws: every stage the run reached, what it
        handled, and what the gate refused; the cells the run measured; and
        the run's shape in a sentence.
    """
    by_stage: dict[str, list[Mapping[str, Any]]] = {}
    for frame in events:
        stage = str(frame.get("stage") or "")
        if stage:
            by_stage.setdefault(stage, []).append(frame)

    stages = [_stage_flow(stage, by_stage[stage]) for stage in by_stage]
    measured = {cell for stage in stages for cell in stage.cells}
    records = max(
        (stage.count for stage in stages if stage.kind == KIND_RECORDS), default=0
    )
    held = max((stage.count for stage in stages if stage.kind == KIND_CELLS), default=0)
    refused = sum(stage.refused for stage in stages)

    return {
        "run_id": run_id,
        "stages": [
            {
                "stage": stage.stage,
                "action": stage.action,
                "count": stage.count,
                "kind": stage.kind,
                "refused": stage.refused,
                "events": stage.events,
            }
            for stage in stages
        ],
        "cells": held,
        "refused": refused,
        "measured": len(measured),
        "records": records,
        "summary": _summary(stages, len(measured), records),
    }


__all__ = [
    "KIND_CELLS",
    "KIND_NONE",
    "KIND_RECORDS",
    "StageFlow",
    "flow_payload",
]
