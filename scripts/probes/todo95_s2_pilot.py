"""TODO95 S2 pilot: calibrate the vision and tabular base boxes.

Measured 2026-11-18: the 375-batch vision base and the 20-epoch iris base,
three control seeds each, one cell cost per family. Writes
``results/sec/pilot.json``; the census reads that file? No -- the map reads a
cell, this reads the base. A bar committed before its control is measured is
post-hoc, so the run writes both and the plan quotes them.
"""

from __future__ import annotations

import json
import math
import time
from pathlib import Path

from computronium.experiment.kernel.evaluate import CellEvaluation, evaluate_cell
from computronium.experiment.registry.task_registry import (
    TaskRegistry,
    primary_pass_bar,
)
from computronium.experiment.sec_loop import _AXIS_DEFAULTS, _coordinate
from computronium.experiment.sec_pilot import BASE_BOXES, base_schedule


def _control(task_id: str, device: str) -> dict[str, float | int | None]:
    schedule = base_schedule(task_id, device)
    if schedule is None:
        raise SystemExit(f"no declared base for {task_id!r}")
    coordinate = _coordinate(dict(_AXIS_DEFAULTS))
    values: list[float] = []
    costs: list[float] = []
    for seed in range(3):
        from dataclasses import replace

        started = time.monotonic()
        evaluation: CellEvaluation = evaluate_cell(
            coordinate, replace(schedule, seed=seed, n_seeds=1)
        )
        costs.append(time.monotonic() - started)
        values.append(float(evaluation.metrics.get("val_acc", math.nan)))
    bar = primary_pass_bar(TaskRegistry().get(task_id))
    mean = sum(values) / len(values)
    return {
        "task": task_id,
        "batch_size": schedule.batch_size,
        "epochs": schedule.epochs,
        "batch_limit": schedule.batch_limit,
        "seeds": values,
        "control_mean": mean,
        "control_std": math.sqrt(sum((v - mean) ** 2 for v in values) / len(values)),
        "bar": None if bar is None else bar.value,
        "floor": None if bar is None else bar.floor,
        "resolution": None if bar is None else bar.resolution,
        "cell_seconds": sum(costs) / len(costs),
    }


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="TODO95 S2 calibration pilot")
    parser.add_argument("--device", default="auto")
    parser.add_argument("--out", type=Path, default=Path("results/sec/pilot.json"))
    args = parser.parse_args()

    rows = [_control(box.task_id, args.device) for box in BASE_BOXES.values()]
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps({"base_boxes": rows}, indent=2, default=str))
    for row in rows:
        cells_per_hour = 3600.0 / float(row["cell_seconds"])
        print(
            f"{row['task']}: control={row['control_mean']:.4f} "
            f"±{row['control_std']:.4f} bar={row['bar']} "
            f"cell={row['cell_seconds']:.1f}s ({cells_per_hour:.0f} cells/h)"
        )
    print(f"-> {args.out}")


if __name__ == "__main__":
    main()
