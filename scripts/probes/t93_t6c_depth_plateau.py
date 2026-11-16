"""Does the plain stack train at the registered depth? (TODO93 T6c)

The pilot reported every arm at val_acc 0.100 at L=32/B=8192/W=1024 with the
loss pinned at 2.2132. A step-budget explanation and a geometry explanation look
identical at 200 steps, so this probe walks the loss curve at 200/500/1000 steps
on the *baseline* arm.

Measured (RTX 3080 10 GiB, CIFAR-10 10k train subset, LR 0.3, seed 11):

    depth=32 steps=200   loss=2.2132 test=0.100   34 s
    depth=32 steps=500   loss=2.2132 test=0.100   85 s
    depth=32 steps=1000  loss=2.2132 test=0.100  171 s

A flat loss over a 5x step budget is a coordinate result about the geometry,
not a step-budget defect: the plain 31-layer Linear+ReLU stack under the default
init does not leave the plateau. L=8 at the same LR and budget reaches 0.419
(TODO93 §2.4, T6c), so the depth rung needs the plan's LayerNorm fallback (c≈2)
or a depth-stable init before any depth claim is registered.

Usage::

    uv run python scripts/probes/t93_t6c_depth_plateau.py --depth 32
"""

from __future__ import annotations

import argparse
import time

from computronium.core.system_trainer import SystemTrainer, SystemTrainerConfig
from computronium.validation import memory_frontier as frontier


def curve(depth: int, lr: float, checkpoints: tuple[int, ...], seed: int) -> None:
    x_train, y_train, x_test, y_test = frontier._cifar()
    point = frontier.PilotPoint(depth=depth, steps=max(checkpoints))
    system = frontier.build_arm("backprop", point, lr=lr, seed=seed)
    trainer = SystemTrainer(
        system=system,
        config=SystemTrainerConfig(
            max_epochs=point.epochs,
            batch_size=point.batch,
            limit_train_batches=point.batches_per_epoch,
            device="cuda",
            seed=seed,
            track_memory=False,
            track_flops=False,
            log_every_n_epochs=0,
        ),
        train_data=frontier._Batches(x_train, y_train, point.batch),
    )
    started = time.perf_counter()
    for target in checkpoints:
        while trainer.global_step < target:
            trainer.train_epoch()
        print(  # ruff: ignore[print] - a probe prints its measurement
            f"depth={depth} lr={lr} steps={trainer.global_step} "
            f"loss={trainer.history[-1]['train_loss']:.4f} "
            f"test={frontier._accuracy(system, x_test, y_test, 'cuda'):.3f} "
            f"{time.perf_counter() - started:.0f}s",
            flush=True,
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--depth", type=int, default=32)
    parser.add_argument("--lr", type=float, default=frontier.FROZEN_LR["backprop"])
    parser.add_argument("--seed", type=int, default=frontier.PILOT_SEEDS[0])
    args = parser.parse_args()
    curve(args.depth, args.lr, (200, 500, 1000), args.seed)
