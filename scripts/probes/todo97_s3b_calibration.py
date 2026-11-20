"""TODO97 S3b: calibrate every declared family base box.

One control per family: the declared base over ``CONTROL_SEEDS`` seeds, the
bar at the task's resolution, the cell's measured cost and the record's replay
hash. ``results/`` is an artifact, so the plan quotes the numbers and this
probe reproduces them; a family that cannot train is reported as a defect
with its error, not skipped.

Run:
    uv run python scripts/probes/todo97_s3b_calibration.py --out results/sec/pilot.json
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from computronium.experiment.kernel.evaluate import evaluate_cell
from computronium.experiment.sec_pilot import (
    BASE_BOXES,
    TASK_FAMILIES,
    base_schedule,
    calibrate_control,
)


def _row(family: str, device: str) -> dict[str, object]:
    box = BASE_BOXES[family]
    schedule = base_schedule(box.task_id, device)
    if schedule is None:
        return {
            "family": family,
            "task": box.task_id,
            "status": "unimplemented",
            "reason": "no base schedule",
        }
    started = time.monotonic()
    try:
        calibration = calibrate_control(schedule, evaluate=evaluate_cell)
    except Exception as exc:  # ruff: ignore[blind-except] - one defect must not end the sweep
        return {
            "family": family,
            "task": box.task_id,
            "status": "defective",
            "error": f"{type(exc).__name__}: {exc}",
            "walltime_s": time.monotonic() - started,
        }
    if calibration is None:
        return {
            "family": family,
            "task": box.task_id,
            "status": "unimplemented",
            "reason": "the task declares no bar",
        }
    bar = calibration.bar
    return {
        "family": family,
        "task": box.task_id,
        "status": "calibrated" if calibration.has_power else "no_power",
        "metric_key": bar.metric_key,
        "direction": bar.direction,
        "bar": bar.value,
        "floor": bar.floor,
        "resolution": bar.resolution,
        "sigma": bar.sigma,
        "control_mean": calibration.control_mean,
        "control_std": calibration.control_std,
        "seeds": calibration.seeds,
        "cell_seconds": calibration.cell_seconds,
        "param_count": calibration.param_count,
        "param_budget": box.param_budget,
        "within_budget": calibration.param_count <= box.param_budget,
        "replay": calibration.replay,
        "walltime_s": time.monotonic() - started,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="TODO97 S3b base calibration")
    parser.add_argument("--device", default="auto")
    parser.add_argument(
        "--family", action="append", choices=TASK_FAMILIES, default=None
    )
    parser.add_argument("--out", type=Path, default=Path("results/sec/pilot.json"))
    args = parser.parse_args()

    families = args.family or list(TASK_FAMILIES)
    rows = [_row(family, args.device) for family in families]
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps({"base_boxes": rows}, indent=2, default=str))
    for row in rows:
        if row["status"] != "calibrated":
            print(f"{row['family']}: {row['status']} — {row}")
            continue
        print(
            f"{row['family']}: {row['task']} "
            f"{row['metric_key']}={row['control_mean']:.4f} "
            f"(bar {row['bar']}, {row['direction']}) "
            f"{row['cell_seconds']:.1f}s {row['replay']}"
        )
    calibrated = sum(row["status"] == "calibrated" for row in rows)
    print(f"-> {args.out}: {calibrated}/{len(rows)} families calibrated")


if __name__ == "__main__":
    main()
