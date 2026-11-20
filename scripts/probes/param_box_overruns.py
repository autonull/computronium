#!/usr/bin/env python
"""TODO97 S6: measure the four parameter-box overruns at their declared boxes.

Each row below was ``defect`` at its family base because the composed network
exceeded the family's parameter ceiling. The declared box is the budget the
mechanism needs on that task; this probe asks whether the count fits it.

Run:
    uv run python scripts/probes/param_box_overruns.py
"""

from __future__ import annotations

import time
from dataclasses import replace
from typing import Final

from computronium.experiment.sec_census import build_census
from computronium.experiment.sec_loop import _iter_legal_coordinates, _train_nearest
from computronium.experiment.sec_pilot import base_schedule

#: (primitive, task, declared box in parameters), from TODO97 §4.3.
BOXES: Final[tuple[tuple[str, str, int], ...]] = (
    ("primitive.credit_assignment.surrogate", "mnist", 300_000),
    ("primitive.geometry.attention", "char_ngram", 600_000),
    ("primitive.geometry.routing", "mnist", 300_000),
    ("primitive.geometry.tile", "mnist", 1_000_000),
    ("primitive.geometry.causal_transformer", "tiny_shakespeare", 600_000),
)


def measure(primitive: str, task: str, budget: int, device: str) -> dict[str, object]:
    """Train the nearest legal box under the declared ceiling, or time out."""
    census = {entry.id: entry for entry in build_census()}
    base = base_schedule(task, device)
    assert base is not None
    schedule = replace(base, param_budget=budget)
    candidates = _iter_legal_coordinates(census[primitive], limit=24, task_id=task)
    started = time.monotonic()
    evaluation, coordinate, error, tried, timed_out = _train_nearest(
        candidates, schedule
    )
    return {
        "primitive": primitive,
        "task": task,
        "declared_box": budget,
        "trained": evaluation is not None,
        "tried": tried,
        "timed_out": timed_out,
        "param_count": None if evaluation is None else evaluation.param_count,
        "params_fit": (evaluation is not None and evaluation.param_count <= budget),
        "val_acc": None if evaluation is None else evaluation.metrics.get("val_acc"),
        "walltime_s": None if evaluation is None else evaluation.walltime_s,
        "elapsed_s": round(time.monotonic() - started, 1),
        "geometry": None if coordinate is None else coordinate.geometry,
        "error": None if error is None else str(error)[:200],
    }


def main() -> None:
    for primitive, task, budget in BOXES:
        row = measure(primitive, task, budget, "cuda")
        print(
            f"{row['primitive']}: {row['task']} box={row['declared_box']:,} "
            f"params={row['param_count']} fits={row['params_fit']} "
            f"val_acc={row['val_acc']} geometry={row['geometry']} "
            f"tried={row['tried']} walltime_s={row['walltime_s']} "
            f"elapsed_s={row['elapsed_s']} error={row['error']}",
            flush=True,
        )


if __name__ == "__main__":
    main()
