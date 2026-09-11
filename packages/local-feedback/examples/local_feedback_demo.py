"""Local-feedback demo — fixed vs adaptive feedback under matched norm.

Arms (X-ALI-001 validated scope, standalone torch form):
    fixed     — random feedback, never updated.
    adaptive  — feedback re-projected onto the normalized forward weight.

Output: per-arm late-half improvement_per_norm, mean feedback alignment, and
final losses. θ-freeze is not applicable here (all weights train locally);
the mechanism claim is descent quality per unit displacement.
"""

from __future__ import annotations

import argparse
import random
import time

import torch
from local_feedback import (
    AdaptiveFeedback,
    FixedFeedback,
    LocalFeedbackTrainer,
    late_half_mean,
)
from torch import nn


def _make_arm(seed: int, adaptive: bool) -> LocalFeedbackTrainer:
    gen = torch.Generator().manual_seed(seed)
    model = nn.Sequential()
    hidden = nn.Linear(16, 32)
    readout = nn.Linear(32, 4)
    with torch.no_grad():
        hidden.weight.normal_(0.0, 0.3, generator=gen)
        hidden.bias.zero_()
        readout.weight.normal_(0.0, 0.3, generator=gen)
        readout.bias.zero_()
    model.add_module("hidden", hidden)
    model.add_module("readout", readout)
    feedback: AdaptiveFeedback = (
        AdaptiveFeedback(32, 4, feedback_lr=1.0, generator=gen)
        if adaptive
        else FixedFeedback(32, 4, generator=gen)
    )
    return LocalFeedbackTrainer(model, feedback, lr=0.05)


def _task(seed: int, n: int = 64) -> tuple[torch.Tensor, torch.Tensor]:
    gen = torch.Generator().manual_seed(seed + 500)
    basis = torch.randn(16, 4, generator=gen) * 2.0
    x = torch.randn(n, 16, generator=gen)
    y = (x @ basis + torch.randn(n, 4, generator=gen) * 0.5).argmax(-1)
    return x, y


def run_arm(
    seed: int, adaptive: bool, steps: int = 60, feedback_lr: float = 0.02
) -> dict[str, object]:
    torch.manual_seed(seed)
    random.seed(seed)
    gen = torch.Generator().manual_seed(seed)
    model = _make_arm(seed, adaptive=False)
    feedback: AdaptiveFeedback = (
        AdaptiveFeedback(32, 4, feedback_lr=feedback_lr, generator=gen)
        if adaptive
        else FixedFeedback(32, 4, generator=gen)
    )
    trainer = LocalFeedbackTrainer(model.model, feedback, lr=0.02)
    x, y = _task(seed)
    losses: list[float] = []
    ipns: list[float] = []
    for _ in range(steps):
        stats = trainer.train_step(x, y)
        losses.append(stats.loss_after)
        ipns.append(stats.improvement_per_norm)
    alignment = trainer.feedback.feedback_alignment(trainer.readout.weight.detach())
    return {
        "losses": losses,
        "improvement_per_norm": ipns,
        "final_loss": losses[-1],
        "late_ipn": late_half_mean(ipns),
        "feedback_alignment": alignment,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()
    t0 = time.perf_counter()
    results = {
        arm: run_arm(args.seed, adaptive=(arm == "adaptive"))
        for arm in ("fixed", "adaptive")
    }
    fixed, adaptive = results["fixed"], results["adaptive"]
    for arm, r in results.items():
        print(
            f"{arm:9s} final_loss={r['final_loss']:.4f} "
            f"late_ipn={r['late_ipn']:.4f} "
            f"feedback_alignment={r['feedback_alignment']:.4f}"
        )
    better = adaptive["late_ipn"] > fixed["late_ipn"]  # type: ignore[operator]
    print(f"adaptive_late_ipn_greater_than_fixed: {better}")
    print(f"walltime: {time.perf_counter() - t0:.3f}s (printed, never recorded)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
