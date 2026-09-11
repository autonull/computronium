"""Psi-PEFT vs SGD readout retraining benchmark (T20.3.6).

Arms: frozen-null, closed-form ridge (ρ=1), temporal_090, adaptive,
buffered, SGD readout retraining. Metrics: phase accuracy, adaptation
walltime, θ SHA invariance. ≥3 seeds; mean ± variance; --quick available.

Validated claim scope (X-TPC-003): under this synthetic conflicting-label
switch at quick budget, temporal-ψ arms match a re-trained linear readout
at matched budget. No universal claim is made.
"""

from __future__ import annotations

import argparse
import time

import torch
from psi_peft.adaptive import AdaptivePsiReadout
from psi_peft.buffered import BufferedPsiReadout
from psi_peft.metrics import Readout, SyntheticTask, theta_sha
from psi_peft.readout import PsiReadout
from torch import Tensor

FEATURE_DIM, NUM_CLASSES, BATCH = 32, 4, 64
EPISODES = {"quick": 10, "full": 40}
SEEDS = {"quick": 3, "full": 3}


class SGDReadout:
    """Gradient-trained linear readout on frozen features (baseline)."""

    def __init__(self, feature_dim: int, num_classes: int, steps: int = 5) -> None:
        self.linear = torch.nn.Linear(feature_dim, num_classes)
        self.opt = torch.optim.Adam(self.linear.parameters(), lr=0.05)
        self.steps = steps

    def update(self, h: Tensor, y: Tensor) -> None:
        for _ in range(self.steps):
            self.opt.zero_grad()
            loss = torch.nn.functional.cross_entropy(self.linear(h.detach()), y)
            loss.backward()
            self.opt.step()

    def forward(self, h: Tensor) -> Tensor:
        return self.linear(h)


def make_readout(arm: str, feature_dim: int, num_classes: int) -> Readout | None:
    match arm:
        case "temporal_090":
            return PsiReadout(feature_dim, num_classes, trace_decay=0.9)
        case "adaptive":
            return AdaptivePsiReadout(feature_dim, num_classes)
        case "buffered":
            return BufferedPsiReadout(
                feature_dim, num_classes, refit_interval=4, drift_threshold=0.6
            )
        case "closed_form":
            return PsiReadout(feature_dim, num_classes, trace_decay=1.0)
        case "sgd_readout":
            return SGDReadout(feature_dim, num_classes)
        case _:
            raise ValueError(f"unknown arm {arm}")


def run_seed(arm: str, seed: int, episodes: int) -> dict[str, float | bool]:
    torch.manual_seed(seed)
    gen = torch.Generator().manual_seed(seed + 1)
    backbone = torch.nn.Sequential(
        torch.nn.Linear(FEATURE_DIM, 64),
        torch.nn.Tanh(),
        torch.nn.Linear(64, FEATURE_DIM),
    )
    frozen_sha = theta_sha(backbone)
    task = SyntheticTask(gen, FEATURE_DIM, NUM_CLASSES)
    readout: Readout | None = (
        None if arm == "frozen_null" else make_readout(arm, FEATURE_DIM, NUM_CLASSES)
    )

    def batch(n: int) -> tuple[Tensor, Tensor]:
        h, y = task.batch(n)
        return backbone(h.detach()), y

    accs: dict[str, float] = {}
    for phase, flip in (("A", False), ("B", True), ("A_ret", False)):
        if flip:
            task.flip()
        start = time.perf_counter()
        for _ in range(episodes):
            h, y = batch(BATCH)
            if readout is not None:
                readout.update(h, y)
        walltime = time.perf_counter() - start
        h_probe, y_probe = batch(512)
        accs[phase] = (
            1.0 / NUM_CLASSES
            if readout is None
            else float(
                (readout.forward(h_probe).argmax(-1) == y_probe).float().mean().item()
            )
        )
        accs[f"{phase}_walltime"] = walltime
    theta_ok = theta_sha(backbone) == frozen_sha
    return {
        "A": accs["A"],
        "B": accs["B"],
        "A_ret": accs["A_ret"],
        "walltime": accs["A_walltime"] + accs["B_walltime"] + accs["A_ret_walltime"],
        "theta_invariant": float(theta_ok),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()
    mode = "quick" if args.quick else "full"
    episodes, seeds = EPISODES[mode], SEEDS[mode]

    arms = [
        "frozen_null",
        "closed_form",
        "temporal_090",
        "adaptive",
        "buffered",
        "sgd_readout",
    ]
    print(f"psi vs sgd readout — mode={mode} episodes={episodes} seeds={seeds}")
    print(
        f"{'arm':14s} {'A':>12s} {'B':>12s} {'A_ret':>12s} {'wall(ms)':>10s} {'θ-inv':>6s}"
    )
    for arm in arms:
        runs = [run_seed(arm, seed, episodes) for seed in range(seeds)]
        row = f"{arm:14s}"
        for key in ("A", "B", "A_ret"):
            vals = [r[key] for r in runs]  # type: ignore[literal-required]
            row += f" {sum(vals) / len(vals):.3f}±{(max(vals) - min(vals)) / 2:.3f}"
        wall = sum(r["walltime"] for r in runs) / len(runs) * 1e3  # type: ignore[operator]
        theta = all(r["theta_invariant"] for r in runs)  # type: ignore[operator]
        print(f"{row} {wall:8.1f}ms {theta!s:>6s}")

    print("scope: synthetic conflicting-label switch, frozen features, quick budget;")
    print("no claim beyond this task and budget (see README validated scope).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
