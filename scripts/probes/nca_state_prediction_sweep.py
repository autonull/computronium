"""NCA state-prediction discriminativeness sweep (TODO23 §12).

One-step targets degenerate to identity (small tanh deltas, next≈states
→ cell_acc 1.0 for trained AND permuted control). Sweep rollout depth k
and teacher delta_scale for a k-step rollout target where the student
trains by BPTT through ``geometry.rollout(grad=True)``; the honest task
must separate trained (≈teacher) from permuted-control (chance).

uv run python scripts/probes/nca_state_prediction_sweep.py
Walltime printed, never recorded.
"""

from __future__ import annotations

import time

import torch
import torch.nn.functional as F  # ruff: ignore[lowercase-imported-as-non-lowercase]
from torch import Tensor

from computronium import GeometryConfig
from computronium.ontology.geometry import geometry_from_config

GRID, CH, BATCH = 10, 4, 32


def nca(seed: int, delta_scale: float):
    torch.manual_seed(seed)
    return geometry_from_config(
        GeometryConfig.nca(
            channels=CH,
            grid_hw=(GRID, GRID),
            label_channels=0,
            delta_scale=delta_scale,
        )
    )


def pair(teacher, seed: int, k: int) -> tuple[Tensor, Tensor]:
    gen = torch.Generator().manual_seed(seed)
    ids = torch.randint(0, CH, (BATCH, GRID, GRID), generator=gen)
    states = F.one_hot(ids, CH).permute(0, 3, 1, 2).float()
    with torch.no_grad():
        nxt = teacher.rollout(states, k)
    return states, nxt


def run(seed: int, k: int, ds: float, epochs: int = 300, lr: float = 0.02) -> None:
    t0 = time.perf_counter()
    torch.manual_seed(seed)
    teacher = nca(seed, ds)
    student = nca(seed + 500, ds)

    def train(label_shuffle: bool) -> float:
        opt = torch.optim.Adam(student.parameters(), lr=lr)
        for ep in range(epochs):
            x, y = pair(teacher, seed * 1000 + ep, k)
            if label_shuffle:
                y = y[
                    torch.randperm(len(y), generator=torch.Generator().manual_seed(ep))
                ]
            opt.zero_grad()
            pred = student.rollout(x, k, grad=True)
            F.mse_loss(pred, y).backward()
            opt.step()
        with torch.no_grad():
            x, y = pair(teacher, seed * 1000 + 9999, k)
            pred = student.rollout(x, k)
            mse = float(F.mse_loss(pred, y))
            return float((pred.argmax(1) == y.argmax(1)).float().mean())

    acc = train(False)
    ctl = train(True)
    print(
        f"seed={seed} k={k} ds={ds}: acc={acc:.3f} control={ctl:.3f} "
        f"(chance 0.25) ({time.perf_counter() - t0:.1f}s)"
    )


for seed in (0, 1, 2):
    run(seed, k=3, ds=0.5)
