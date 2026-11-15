"""TODO92 §3.10: pilot and ladder runner for the credit × substrate 2×2.

The interaction is `(PEPITA − gradient)_substrate − (PEPITA − gradient)_digital`
at L2/20 on MNIST, where PEPITA is legal on feedforward geometry. This probe
prices the cell and runs the AGENTS viability ladder before the claim-grade 2×2.

- ``--mode pilot``: one seed, one epoch, both credits on digital and the chosen
  substrate. Answers rung 1 (does it train?) and measures the per-epoch cost.
- ``--mode ladder``: three ``update.step_size`` points, one seed each, plus a
  confirmation seed at the best point. Answers the viability gate; it is a
  screening map, not a claim.

The two arms start from the recorded §3.7 anchors, so only the credit,
substrate, step size and seed change. Walltime printed, never recorded.

Measured 2026-11-15 (pilot, seed 47, 1 epoch, CPU): gradient digital 0.9548
(15.2 s) / analog 0.9525 (20.1 s); PEPITA digital 0.9524 (21.5 s) / analog
0.9512 (23.2 s). All above chance (0.10); ~20 s/epoch.

Run: uv run python scripts/probes/t92_credit_substrate_pilot.py
     uv run python scripts/probes/t92_credit_substrate_pilot.py --mode ladder
"""

from __future__ import annotations

import argparse
import time
from dataclasses import replace
from pathlib import Path

from computronium.experiment.evidence.store import RecordStore, StoreConfig
from computronium.experiment.kernel.evaluate import evaluate_cell
from computronium.experiment.schema.coordinate import Coordinate, Schedule

__all__ = ["main"]

ROOT = Path(__file__).resolve().parents[2]
ARMS: dict[str, tuple[str, str]] = {
    "gradient": ("experiments/experiment_20261109_103319.duckdb", "bfab4794"),
    "pepita": ("experiments/experiment_20261109_165912.duckdb", "9a54fb36"),
}
LADDER: tuple[float, ...] = (3e-4, 1e-3, 3e-3)


def _locate(arm: str) -> tuple[Coordinate, Schedule]:
    store_name, anchor = ARMS[arm]
    with RecordStore(StoreConfig(path=ROOT / store_name, read_only=True)) as store:
        for record in store.query_records():
            if record.measurement_key.startswith(anchor):
                return Coordinate.from_record(record), record.schedule
    msg = f"no record {anchor} in {store_name}"
    raise LookupError(msg)


def _cell(
    arm: str,
    substrate: str,
    seed: int,
    epochs: int,
    step_size: float | None,
    device: str,
) -> tuple[float, float]:
    coordinate, schedule = _locate(arm)
    params = dict(coordinate.params)
    if step_size is not None:
        params["update.step_size"] = step_size
    run = replace(coordinate, substrate=substrate, params=params)
    started = time.perf_counter()
    result = evaluate_cell(
        run, replace(schedule, seed=seed, epochs=epochs, device=device)
    )
    return result.metrics["val_acc"], time.perf_counter() - started


def _print(
    arm: str,
    substrate: str,
    seed: int,
    epochs: int,
    step: float | None,
    device: str,
) -> float:
    value, wall = _cell(arm, substrate, seed, epochs, step, device)
    label = f"step={step if step is not None else 'default'}"
    print(
        f"{arm:9} {substrate:7} seed={seed:2} {label:14} "
        f"val_acc={value:.4f} ({wall:.1f}s) {device}"
    )
    return value


def _pilot(seed: int, epochs: int, device: str) -> int:
    for substrate in ("digital", "analog"):
        for arm in ARMS:
            _print(arm, substrate, seed, epochs, None, device)
    return 0


def _ladder(seed: int, epochs: int, device: str) -> int:
    best: tuple[float, float] | None = None
    for step in LADDER:
        value = _print("pepita", "analog", seed, epochs, step, device)
        if best is None or value > best[0]:
            best = (value, step)
    assert best is not None
    confirmation = best[1]
    print(f"best ladder point: step={confirmation} (val_acc={best[0]:.4f})")
    _print("pepita", "analog", seed + 100, epochs, confirmation, device)
    _print("gradient", "analog", seed + 100, epochs, confirmation, device)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("pilot", "ladder"), default="pilot")
    parser.add_argument("--seed", type=int, default=47)
    parser.add_argument("--epochs", type=int, default=1)
    parser.add_argument("--device", default="cpu")
    args = parser.parse_args()
    if args.mode == "ladder":
        return _ladder(args.seed, args.epochs, args.device)
    return _pilot(args.seed, args.epochs, args.device)


if __name__ == "__main__":
    raise SystemExit(main())
