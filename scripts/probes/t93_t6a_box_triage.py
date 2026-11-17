"""T6a box triage: is the refusal a box artifact, or the claim's coordinate?

The registration refused the memory claim at L=4→8 (hybrid 1.22× the
checkpointed arm's activation set). T6b's lock states the same ratio at
**L=32** (0.48×). Measured at W=512/B=4096, seed 21, 4 steps, the ratio is
depth-dependent: **1.25 / 0.72 / 0.48** at L=8/16/32 — so a refusal at L=8
measures the OOM guard's box, not the claim's geometry.

This probe asks the other half: at L=16, does the plain arm still train
(floor 0.375) and does the hybrid hold ≤0.5× at a matched accuracy? If both
hold, the refusal is a **box artifact** and the claim has a measured
coordinate at L=16; if either fails, it is a defect or a real refusal.

Measured regime: CIFAR-10 10k/10k, W=512, B=4096, 200 steps, L=16, LR 0.3,
seeds 21 and the disjoint confirmation 22, RTX 3080 10 GiB (~350 MB peak).
Informative for TODO93 T6a (2026-11-17).
"""

from __future__ import annotations

import json

import torch

from computronium.validation.memory_frontier import (
    PilotPoint,
    cifar_splits,
    measure_cell,
)

__all__ = ["main"]

ARMS = ("backprop", "backprop+ckpt", "hybrid")
DEPTH = 16


def main() -> None:
    x_train, y_train, x_test, y_test = cifar_splits()
    point = PilotPoint(depth=DEPTH, width=512, batch=4096, steps=200)
    for seed in (21, 22):
        for arm in ARMS:
            cell = measure_cell(
                arm,
                point,
                lr=0.3,
                seed=seed,
                device="cuda",
                x_train=x_train,
                y_train=y_train,
                x_test=x_test,
                y_test=y_test,
            )
            print(
                json.dumps({
                    "depth": DEPTH,
                    "seed": seed,
                    "arm": arm,
                    "val_acc": round(cell.val_acc, 4),
                    "act_mb": round(cell.activations_mb or 0.0, 1),
                    "peak_mb": round(cell.peak_mb or 0.0, 1),
                })
            )
            torch.cuda.empty_cache()


if __name__ == "__main__":
    main()
