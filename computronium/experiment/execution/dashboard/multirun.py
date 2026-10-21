"""Several runs' evidence in one space (TODO69).

One run is one answer to one question, and a store holds more than one run:
the run, the runs its own answers spawned, and the runs a reader has put
side by side. The dashboard shows one of them at a time — a picture can only
show one — but the *space* is shared: the runs measured cells of the same
declared space, and where each of them reached is a question about the
space rather than about one run.

The answer is read here, on the server, from the same ``declared_space`` the
map reads: every run's slice of the space, the cells it measured in it, and
the cells the system refuses. The browser draws the union of those slices
and colours the cells by the run that measured them, so a reader can see
where one run went and another did not.

A cell of one run is not a cell of another unless the two runs held the
same axes at the same values: a slice is a window, and two windows are not
the same window. The payload carries what each run held, so the picture can
say when two runs are not being compared like for like.
"""

from __future__ import annotations

import statistics
import threading
from typing import TYPE_CHECKING, Any

from computronium.experiment.execution.dashboard.space import (
    axis_values,
    declared_space,
)

if TYPE_CHECKING:
    from collections.abc import Sequence

    from computronium.experiment.evidence.store import RecordStore
    from computronium.experiment.schema.axis import StructuralAxis
    from computronium.experiment.schema.record import Record

# How many runs one picture holds.
MAX_RUNS = 4

# The metric a run's cells are read on: the accuracy the dashboard's own
# panels read, so the picture and the panels cannot disagree.
ACCURACY = "val_acc"


def cell_key(values: Sequence[str]) -> str:
    """The name of a cell of the space, in the order the axes are given."""
    return "|".join(values)


def measured_cells(
    records: Sequence[Record],
    axes: Sequence[StructuralAxis],
    metric: str = ACCURACY,
) -> dict[str, dict[str, Any]]:
    """The cells a run measured, and what each of them measured.

    Args:
        records: The run's records.
        axes: The axes the picture shows, in the order it shows them.
        metric: The payload key to summarise.

    Returns:
        One entry per cell: its mean over the seeds measured, how many seeds
        measured it, and the credit rule that measured it.
    """
    values: dict[str, list[float]] = {}
    arms: dict[str, str] = {}
    for record in records:
        key = cell_key([getattr(record, axis.value, "") for axis in axes])
        measured = record.payload.get(metric)
        if isinstance(measured, bool) or not isinstance(measured, int | float):
            continue
        values.setdefault(key, []).append(float(measured))
        arms.setdefault(key, record.credit)
    return {
        key: {
            "accuracy": statistics.fmean(measured),
            "seeds": len(measured),
            "arm": arms.get(key, ""),
        }
        for key, measured in values.items()
    }


def run_slice(
    store: RecordStore,
    run_id: str,
    axes: Sequence[StructuralAxis],
    metric: str = ACCURACY,
    records: Sequence[Record] | None = None,
) -> dict[str, Any] | None:
    """One run's slice of the space, and the cells it measured in it.

    Args:
        store: The store the runs wrote to.
        run_id: The run to read.
        axes: The axes the picture shows, in the order it shows them.
        metric: The payload key to summarise.
        records: The run's records, when the caller has already read them.

    Returns:
        The run's own window on the space — the values it shows on each axis,
        the axes it held, the cells it refused, the cells it measured — or
        ``None`` when the store does not hold the run.
    """
    info = store.query_run(run_id)
    if info is None:
        return None
    if records is None:
        records = list(store.query_records(run_id=run_id))
    spec = info.spec

    task = spec.task_names[0] if spec and spec.task_names else None
    if not task and records:
        task = records[0].schedule.task_id or None

    space = declared_space(spec, records, axes, task=task)
    refused = [
        cell_key([cell["coordinate"].get(axis.value, "") for axis in axes])
        for cell in space["cells"]
        if cell["status"] == "void"
    ]

    return {
        "run_id": run_id,
        "profile": spec.profile if spec else None,
        "status": info.status,
        "started_at": info.started_at.isoformat() if info.started_at else None,
        "records": len(records),
        "values": space["values"],
        "held": space["held"],
        "declared": space["declared"],
        "refused": refused,
        "measured": measured_cells(records, axes, metric),
    }


class SpaceReader:
    """The space of the store's runs, read once and kept.

    Reading a slice is expensive: the system's own void rules are evaluated
    for every cell of it, and a slice holds hundreds of cells. The rules do
    not change, a run's declaration does not either, and a run that measured
    something new has more records — so a slice is read once per run and per
    set of axes, and read again when the run's own evidence grows.

    The store is handed in rather than held: DuckDB's connection belongs to
    the thread that opened it.
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._slices: dict[tuple[str, tuple[str, ...], int], dict[str, Any]] = {}

    def slice(
        self,
        store: RecordStore,
        run_id: str,
        axes: Sequence[StructuralAxis],
        metric: str = ACCURACY,
    ) -> dict[str, Any] | None:
        """One run's slice, read now or taken from what was read before."""
        records = list(store.query_records(run_id=run_id))
        key = (run_id, tuple(axis.value for axis in axes), len(records))
        with self._lock:
            cached = self._slices.get(key)
        if cached is not None:
            return cached
        fresh = run_slice(store, run_id, axes, metric, records=records)
        if fresh is None:
            return None
        with self._lock:
            self._slices[key] = fresh
        return fresh

    def runs(self, store: RecordStore, limit: int = MAX_RUNS) -> list[str]:
        """The runs worth a picture: the newest that measured something."""
        chosen: list[str] = []
        for info in store.query_runs():
            if store.count_records(run_id=info.run_id):
                chosen.append(info.run_id)
            if len(chosen) >= limit:
                break
        return chosen


def union_values(
    runs: Sequence[dict[str, Any]],
    axes: Sequence[StructuralAxis],
) -> dict[str, list[str]]:
    """The values the runs' slices take between them, in the registry's order.

    The order is the registry's, so the picture's columns are the same
    columns whichever runs are in it.
    """
    union: dict[str, list[str]] = {}
    for axis in axes:
        seen: set[str] = set()
        for run in runs:
            seen.update(run["values"].get(axis.value, []))
        union[axis.value] = [value for value in axis_values(axis) if value in seen]
    return union


def agreement(runs: Sequence[dict[str, Any]]) -> tuple[int, int]:
    """How many cells the runs measured between them, and how many they met in."""
    counts: dict[str, int] = {}
    for run in runs:
        for key in run["measured"]:
            counts[key] = counts.get(key, 0) + 1
    return len(counts), sum(1 for count in counts.values() if count > 1)


def summary(runs: Sequence[dict[str, Any]]) -> str:
    """What the runs did between them, in one sentence.

    The sentence says how many runs there were, how many cells they
    measured between them, and whether they met: a reader looking at a
    picture of several runs wants to know whether the runs agree.
    """
    if not runs:
        return "No run in the store has measured anything yet."
    measured, shared = agreement(runs)
    if len(runs) == 1:
        return f"One run measured {measured} cells of the space."
    if shared:
        return (
            f"{len(runs)} runs measured {measured} cells between them, "
            f"and met in {shared}."
        )
    return (
        f"{len(runs)} runs measured {measured} cells between them, and met in "
        f"none: each went where the other did not."
    )


def multirun_payload(
    reader: SpaceReader,
    store: RecordStore,
    axes: Sequence[StructuralAxis],
    *,
    run_ids: Sequence[str] | None = None,
    limit: int = MAX_RUNS,
    metric: str = ACCURACY,
) -> dict[str, Any]:
    """Several runs' evidence in one space.

    Args:
        reader: The reader that holds what it has already read of the store.
        store: The store the runs wrote to.
        axes: The axes the picture shows, in the order it shows them.
        run_ids: The runs to show; the newest that measured when omitted.
        limit: How many runs one picture holds.
        metric: The payload key to summarise.

    Returns:
        The union of the runs' slices, each run's own window on it, the
        cells each of them measured, and the sentence that says what they
        did between them. The payload carries:

        - ``axes`` — the three axes the picture shows;
        - ``values`` — the values the union of the runs' slices takes on
          each of them, in the registry's order;
        - ``runs`` — each run's own window: the values it shows, the axes it
          held, the cells it refused, the cells it measured, and what it
          measured in them;
        - ``counts`` — how many runs there are, how many cells they
          measured between them, how many of those they met in, and how many
          measurements they hold in all;
        - ``summary`` — what the runs did between them, in one sentence.
    """
    chosen = list(run_ids) if run_ids else reader.runs(store, limit)
    runs = [
        slice_
        for slice_ in (reader.slice(store, run_id, axes, metric) for run_id in chosen)
        if slice_ is not None
    ]
    measured, shared = agreement(runs)

    return {
        "axes": [axis.value for axis in axes],
        "values": union_values(runs, axes),
        "runs": runs,
        "counts": {
            "runs": len(runs),
            "measured": measured,
            "shared": shared,
            "cells": sum(len(run["measured"]) for run in runs),
        },
        "summary": summary(runs),
    }


__all__ = [
    "ACCURACY",
    "MAX_RUNS",
    "SpaceReader",
    "agreement",
    "cell_key",
    "measured_cells",
    "multirun_payload",
    "run_slice",
    "summary",
    "union_values",
]
