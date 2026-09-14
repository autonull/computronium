"""TODO25 D.2: calibrate the flat_classification_hard operating point.

Informs the ``HARD_TASK_PARAMS`` constants in ``computronium_lab.lab`` and
the ``flat_classification_hard`` corpus class (H24.2 round 3): the
calibrated quick tier (scale 1.2, noise 1.5, 32x4) saturates 6 catalog
rows at 1.0 accuracy by 20 epochs, censoring rank-based hypothesis
statistics. The sweep trains catalog rows directly per candidate
(scale, noise) at the recorded dims (64 x 8) — NOT through
``CampaignFitness``, whose hard path pins the constants under test.

Selection rule: no row at >= 0.995 (non-saturating), weak rows above the
8-class collapse ceiling (~0.17), top row below 1.0 with headroom.

Round-1 note: candidates with SNR (scale/noise) far below the flat tier's
0.8 collapsed every row to a constant class; round 2 sweeps SNR 0.6-0.75.

Usage: uv run python scripts/probes/todo25_hard_task.py
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import torch
from computronium_lab import Lab
from computronium_lab.lab import synthetic_task
from computronium_lab.research.autopoiesis import (
    CampaignFitness,
    CoordinateGenome,
    NotTrainableError,
)
from computronium_lab.research.corpus import _row
from computronium_lab.synthesis.spec import Constraints, ProblemSpec
from computronium_lab.training import TrainOptions

EPOCHS = 20
SEED = 0
ROWS = ("backprop_mlp", "pepita_mlp", "ff_mlp", "fa_mlp", "ntm_classifier")
CANDIDATES: tuple[tuple[float, float], ...] = (
    (1.2, 1.5),
    (1.2, 1.7),
    (1.5, 1.8),
    (1.4, 1.6),
)
HARD_DIMS = (64, 8)
OUT = Path("scratch/todo25_hard_task.json")


def main() -> int:
    torch.set_num_threads(4)
    report: dict[str, Any] = {"trainability_flat": {}, "sweep": []}

    flat_spec = ProblemSpec(
        task="flat_classification", dataset="gaussian_blob", constraints=Constraints()
    )
    fitness = CampaignFitness(flat_spec)
    for name in ("temporal_psi_task_switcher", "nca_predictor"):
        genome = CoordinateGenome.seed(name, flat_spec)
        try:
            fitness.evaluate(genome, Lab(), seeds=(SEED,), epochs=1)
        except NotTrainableError as exc:
            report["trainability_flat"][name] = f"NotTrainableError: {exc}"
        except Exception as exc:  # ruff: ignore[try-consider-else]  documenting the raw legacy failure mode
            report["trainability_flat"][name] = f"{type(exc).__name__}: {exc}"

    for scale, noise in CANDIDATES:
        spec = ProblemSpec(
            task="flat_classification_hard",
            dataset="gaussian_blob_hard",
            constraints=Constraints(),
            input_dim=HARD_DIMS[0],
            num_classes=HARD_DIMS[1],
        )
        entry: dict[str, Any] = {"scale": scale, "noise": noise, "rows": {}}
        lab = Lab(seed=SEED)
        for name in ROWS:
            system = _row(name).build(spec)
            train_loader, val_loader = synthetic_task(
                seed=SEED,
                input_dim=HARD_DIMS[0],
                num_classes=HARD_DIMS[1],
                scale=scale,
                noise=noise,
            )
            try:
                result = lab.train(
                    system,
                    task="synthetic",
                    epochs=EPOCHS,
                    spec=spec,
                    options=TrainOptions(stability_guard=True),
                    val_data=val_loader,
                    train_data=train_loader,
                )
            except Exception as exc:
                entry["rows"][name] = f"skipped: {type(exc).__name__}"
                continue
            metrics = result.metrics
            acc = float(metrics.get("val_acc", metrics.get("accuracy", 0.0)))
            entry["rows"][name] = round(acc, 4)
            print(f"({scale}, {noise}) {name}: {acc:.3f}", flush=True)
        report["sweep"].append(entry)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(report["sweep"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
