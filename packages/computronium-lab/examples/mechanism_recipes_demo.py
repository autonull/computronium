"""Mechanism recipes demo — temporal ψ, adaptive feedback, role-split.

Each recipe is instantiated from its validated construction path and used in
its validated scope; results are printed, never recorded.
"""

from __future__ import annotations

import argparse
import time
from typing import TYPE_CHECKING

import torch
from computronium_lab import Lab
from computronium_lab.recipes import build_recipe

if TYPE_CHECKING:
    from local_feedback import AdaptiveFeedback
    from psi_peft import AdaptivePsiReadout


def _temporal_psi_segment(lab: Lab) -> None:
    """Fit the temporal-ψ readout on a frozen-feature task, then flip it."""

    readout: AdaptivePsiReadout = build_recipe(  # type: ignore[assignment]
        "temporal_psi", feature_dim=64, num_classes=4
    )
    gen = torch.Generator().manual_seed(lab.seed)
    basis = torch.randn(64, 4, generator=gen) * 3.0
    probe = torch.randn(64, 64, generator=gen)
    for phase in ("task_A", "task_B_conflict"):
        sign = 1.0 if phase == "task_A" else -1.0
        for _ in range(8):
            h = torch.randn(32, 64, generator=gen)
            y = ((h @ basis) * sign).argmax(-1)
            readout.update(h, y)
        y = ((probe @ basis) * sign).argmax(-1)
        acc = float((readout.forward(probe).argmax(-1) == y).float().mean())
        print(f"temporal_psi {phase}: probe acc={acc:.2f}")


def _adaptive_feedback_segment(lab: Lab) -> None:

    fb: AdaptiveFeedback = build_recipe(  # type: ignore[assignment]
        "adaptive_feedback", in_features=32, out_features=4, feedback_lr=1.0
    )
    w = torch.randn(4, 32)
    fb.update(w)
    print(
        f"adaptive_feedback: alignment after per-step re-projection = "
        f"{fb.feedback_alignment(w):.3f} (1.0; slow blend converges there too)"
    )


def _role_split_segment(lab: Lab) -> None:
    from computronium_lab.recipes import build_recipe

    system = build_recipe("role_split_muon_readout")
    xs = torch.randn(16, 32)
    ys = torch.randint(0, 4, (16,))
    metrics = system.train_step(xs, ys)
    print(
        f"role_split_muon_readout: one-step loss {metrics.get('loss', float('nan')):.4f}"
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()
    lab = Lab(seed=args.seed)
    t0 = time.perf_counter()
    _temporal_psi_segment(lab)
    _adaptive_feedback_segment(lab)
    _role_split_segment(lab)
    print(f"walltime: {time.perf_counter() - t0:.2f}s (printed, never recorded)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
