"""Triage the T6a refusal: is the hybrid's L=8 cell an implementation defect?

Measured regime: CIFAR-10 10k-image train subset / 10k test, **W=64, B=128,
200 steps**, L=8, LR 0.1/0.3, ladder seed 21, RTX 3080 10 GiB (fits in <1 GB).

Three rung-0 checks, all cheap:

1. does the hybrid learn at this box (label channel, credit update)?
2. does its activation set behave as its owned free pass says (T6b's 0.37×)?
3. is the registration's 1.22× and 0.167 reproduced only at the larger box?

Informative for TODO93 T6a's refusal (2026-11-17) and T6c's re-open.
"""

from __future__ import annotations

import json

import torch

from computronium.validation.memory_frontier import (
    PilotPoint,
    _cifar,
    _measure,
    build_arm,
)

__all__ = ["main"]


def main() -> None:
    device = "cuda"
    x_train, y_train, x_test, y_test = _cifar()
    for width, batch in ((64, 128), (512, 2048)):
        point = PilotPoint(depth=8, width=width, batch=batch, steps=200)
        for lr in (0.1, 0.3):
            for arm in ("backprop", "backprop+ckpt", "hybrid"):
                cell = _measure(
                    arm,
                    point,
                    lr=lr,
                    seed=21,
                    device=device,
                    x_train=x_train,
                    y_train=y_train,
                    x_test=x_test,
                    y_test=y_test,
                )
                print(
                    json.dumps({
                        "width": width,
                        "batch": batch,
                        "arm": arm,
                        "lr": lr,
                        "val_acc": round(cell.val_acc, 3),
                        "peak_mb": round(cell.peak_mb or 0.0, 1),
                        "act_mb": round(cell.activations_mb or 0.0, 1),
                        "share": round(cell.activation_share or 0.0, 3),
                    })
                )
                torch.cuda.empty_cache()
    # Does the hybrid's free pass exist and return one readout tensor?
    system = build_arm(
        "hybrid", PilotPoint(depth=8, width=64, batch=128), lr=0.3, seed=21
    )
    x = x_train[:128].to(device)
    acts = system.credit.free_activations(system.substrate, system.geometry, x)
    print(
        json.dumps({
            "owned_free": list(acts.shape),
            "params": len(system.geometry.params),
        })
    )


if __name__ == "__main__":
    main()
