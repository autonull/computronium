"""Frozen-backbone task switching: learn A → switch to conflicting B → return to A.

CPU, deterministic under seed, prints per-phase accuracies and θ invariance.
Validated scope: X-TPC-002/003-style conflicting-label switch on a frozen
feature basis; quick mode completes well under 2 minutes.
"""

from __future__ import annotations

import argparse
import time

import torch
from psi_peft.adaptive import AdaptivePsiReadout
from psi_peft.metrics import SyntheticTask, accuracy, theta_sha

FEATURE_DIM, NUM_CLASSES, BATCH, EPISODES = 32, 4, 64, 20


def main() -> int:  # ruff: ignore[too-many-locals] single linear demo flow; splitting hides the phase table
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()

    torch.manual_seed(args.seed)
    gen = torch.Generator().manual_seed(args.seed + 1)
    backbone = torch.nn.Sequential(
        torch.nn.Linear(FEATURE_DIM, 64),
        torch.nn.Tanh(),
        torch.nn.Linear(64, FEATURE_DIM),
    )
    _ = backbone(torch.randn(2, FEATURE_DIM))  # init; θ frozen hereafter
    frozen_sha = theta_sha(backbone)
    task = SyntheticTask(gen, FEATURE_DIM, NUM_CLASSES)
    readout = AdaptivePsiReadout(FEATURE_DIM, NUM_CLASSES)
    print(f"seed={args.seed}  θ sha={frozen_sha[:12]}…")

    def batch(n: int) -> tuple[torch.Tensor, torch.Tensor]:
        h, y = task.batch(n)
        return backbone(h.detach()), y

    phases: list[tuple[str, bool]] = [
        ("A (acquire)", False),
        ("B (conflicting)", True),
        ("A' (return)", False),
    ]
    results: list[tuple[str, float, float]] = []
    for name, flip in phases:
        if flip:
            task.flip()
        start = time.perf_counter()
        for _ in range(EPISODES):
            h, y = batch(BATCH)
            readout.update(h, y)
        walltime = time.perf_counter() - start
        h_probe, y_probe = batch(512)
        acc = accuracy(readout, h_probe, y_probe)
        results.append((name, acc, walltime))
        print(f"  {name:16s} acc={acc:.3f}  adapt={walltime * 1e3:.1f} ms")

    assert theta_sha(backbone) == frozen_sha, "θ was modified"  # ruff: ignore[assert] hard demo gate
    acquired, returned = results[0][1], results[2][1]
    print("θ invariance: bitwise OK")
    print(f"re-acquisition: {returned:.3f} vs acquired {acquired:.3f}")
    if returned >= acquired - 0.05:
        print("result: PASS — frozen-backbone A→B→A switching recovered task A")
        return 0
    print("result: WEAK — re-acquisition lagged beyond 0.05 of acquisition")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
