"""NCA state-prediction feasibility (TODO23 §12: the NCA row's blocker).

Task: hidden-teacher transition prediction. A fixed random NCA (teacher,
deterministic per seed, full mask) defines the one-step map on (B, C, H,
W) one-hot state grids; a student NCA (same shape, fresh weights) trains
by direct autograd MSE through geometry.forward (credit axis bypassed —
one-step MSE through the geometry IS backprop, the same honest framing
as sequential.train_sequence). Metrics: MSE + per-cell argmax accuracy
vs the one-hot target encoding.

uv run python scripts/probes/nca_state_prediction.py
Walltime printed, never recorded.
"""

from __future__ import annotations

import time

import torch
import torch.nn.functional as F  # ruff: ignore[lowercase-imported-as-non-lowercase]
from torch import Tensor

from computronium import GeometryConfig, NcaGeometry
from computronium.ontology.geometry import geometry_from_config

GRID, CH, BATCH = 10, 4, 32


def teacher_rule(seed: int) -> NcaGeometry:
    torch.manual_seed(seed)
    g = geometry_from_config(
        GeometryConfig.nca(channels=CH, grid_hw=(GRID, GRID), label_channels=0)
    )
    for p in g.parameters():
        p.requires_grad_(False)
    return g  # type: ignore[return-value]


def batch(teacher: NcaGeometry, seed: int) -> tuple[Tensor, Tensor]:
    g = torch.Generator().manual_seed(seed)
    ids = torch.randint(0, CH, (BATCH, GRID, GRID), generator=g)
    states = F.one_hot(ids, CH).permute(0, 3, 1, 2).float()
    ones = torch.ones(BATCH, GRID, GRID)
    with torch.no_grad():
        nxt = teacher.step(states, mask=ones)
    return states, nxt


def run(seed: int, epochs: int = 200, lr: float = 0.02) -> None:
    t0 = time.perf_counter()
    torch.manual_seed(seed)
    teacher = teacher_rule(seed)
    student = geometry_from_config(
        GeometryConfig.nca(channels=CH, grid_hw=(GRID, GRID), label_channels=0)
    )
    opt = torch.optim.Adam(student.parameters(), lr=lr)  # type: ignore[attr-defined]
    for _ in range(epochs):
        x, y = batch(teacher, seed * 1000 + _)
        pred = student.forward(x)
        loss = F.mse_loss(pred, y)
        opt.zero_grad()
        loss.backward()
        opt.step()
    with torch.no_grad():
        x, y = batch(teacher, seed * 1000 + 9999)
        pred = student.forward(x)
        mse = float(F.mse_loss(pred, y))
        acc = float((pred.argmax(1) == y.argmax(1)).float().mean())
    print(
        f"seed={seed} mse={mse:.5f} cell_acc={acc:.3f} ({time.perf_counter() - t0:.1f}s)"
    )


for s in (0, 1, 2):
    run(s)
