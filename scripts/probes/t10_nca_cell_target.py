"""T10: NCA's third error-aware credit — cell-mode target inversion.

T9's cell fold gave ``random_projections`` a readout error on cell rows. The
same fold carries a *target*: the sample-mode one-hot output target folds back
to one row per cell, and the shared cell MLP then receives per-cell targets
(``_fold_cell_targets``). That makes ``target_inversion`` a third error-aware
credit on nca × instantaneous, measured against the ``gradient`` control on
digits 8x8 (10 classes, chance 0.10).

Run: uv run python scripts/probes/t10_nca_cell_target.py
Measured (2026-11-12, 20 epochs, 3 seeds, digits 8x8; 360 held-out rows,
resolution 1/360 = 0.0028, majority 0.1306, chance 0.10):
- nca/target_inversion ... (see output)
- nca/gradient control ... (see output)

Locks: ``tests/unit/core/test_credit.py::TestCellModeTargetInversion`` (hiding
the fold leaves every target None → all-zero pseudo-gradients) and
``tests/property/test_dry_run_gate_lock.py::test_target_inversion_accepts_nca_digits``.
"""

from __future__ import annotations

import json
import statistics
import time

import torch

from computronium.core.system_trainer.config import SystemTrainerConfig
from computronium.core.system_trainer.train_task import train_on_task
from computronium.domains.factory import create_task
from computronium.experiment.kernel.compose import compose_cell_system
from computronium.experiment.schema.coordinate import Coordinate

__all__ = ["main"]

EPOCHS = 20
SEEDS = (0, 1, 2)
TASK = "digits"
ARMS = ("target_inversion", "gradient")


def _coordinate(credit: str) -> Coordinate:
    return Coordinate(
        substrate="digital",
        geometry="nca",
        dynamics="instantaneous",
        plasticity="null",
        credit=credit,
        update="adam",
        params={},
    )


def _run_arm(credit: str, seed: int) -> float:
    torch.manual_seed(seed)
    task = create_task(TASK, device="cpu", quick_mode=True)
    task.setup()
    cell = compose_cell_system(
        coordinate=_coordinate(credit),
        geometry={"hidden_dim": 64},
        input_shape=task.input_dim
        if isinstance(task.input_dim, tuple)
        else (1, task.input_dim),
        output_dim=task.output_dim,
    )
    train_on_task(
        lambda _input_dim, _output_dim: cell.system,
        task,
        SystemTrainerConfig(
            max_epochs=EPOCHS,
            device="cpu",
            track_energy=False,
            track_flops=False,
            track_memory=False,
            log_every_n_epochs=1,
        ),
    )
    return task.evaluate(cell.system).accuracy


def _ruler() -> dict[str, float]:
    """Held-out resolution and the majority rate it is measured against."""
    task = create_task(TASK, device="cpu", quick_mode=True)
    task.setup()
    _x, y = task.get_batch("test", batch_size=10_000)
    counts = torch.bincount(y)
    return {
        "held_out": float(y.numel()),
        "resolution": round(1.0 / y.numel(), 5),
        "majority_baseline": round(float(counts.max()) / y.numel(), 4),
    }


def main() -> int:
    started = time.perf_counter()
    results: dict[str, object] = {}
    for credit in ARMS:
        accuracies = [_run_arm(credit, seed) for seed in SEEDS]
        results[credit] = {
            "accuracy": round(statistics.fmean(accuracies), 4),
            "se": round(statistics.stdev(accuracies) / len(accuracies) ** 0.5, 4),
            "seeds": [round(a, 4) for a in accuracies],
        }
        print(f"{credit}: {results[credit]}", flush=True)
    results["ruler"] = _ruler()
    results["walltime_s"] = round(time.perf_counter() - started, 1)
    print(json.dumps(results, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
