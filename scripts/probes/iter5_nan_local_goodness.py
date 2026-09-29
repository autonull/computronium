#!/usr/bin/env python3
"""Regime probe: NaN loss on feedforward x local_goodness (spiral, Iteration 5).

Measured regime (artifacts/broad_map_mt/spiral KB, 2026-09-28, 30-batch L0 cells):
    predictive_settling x local_goodness x unit_rms, depth=1, hidden=512
        -> final_loss=nan, spectral_radius=nan
    lazy x local_goodness x mean_norm, depth=2, hidden=35
        -> final_loss=nan

Isolation (this probe, 25-batch prefix, seed 42):
    predictive_settling @ step_size 0.1, hidden=512 -> loss 1.8e22 at batch 0
        (update-rule independent: unit_rms and euclidean both diverge)
    predictive_settling @ step_size <= 0.01, hidden=512 -> 0.47-0.49, stable
    predictive_settling @ step_size 0.1, hidden=64  -> 0.48, stable
    lazy x local_goodness x mean_norm, hidden=512 -> spikes to 2.9e8;
        the ("lazy", "local_goodness") = 0.1 override holds the max at 0.46

    Both cells still reach nan over a *full* epoch, so a step-size change alone
    does not close the case: the remaining growth is open work.

Run: uv run python scripts/probes/iter5_nan_local_goodness.py
"""

from __future__ import annotations

import math

from computronium.autoscientist.compose import compose_cell_system
from computronium.core.system_trainer.train_task import train_task
from computronium.utils import seed_everything

CASES = [
    ("predictive_settling", "local_goodness", "unit_rms", 1, 512),
    ("lazy", "local_goodness", "mean_norm", 2, 35),
]


def probe(dyn: str, credit: str, upd: str, depth: int, hidden: int) -> dict[str, float]:
    seed_everything(42)

    def factory(input_dim: int, output_dim: int):
        return compose_cell_system(
            dynamics=dyn,
            credit=credit,
            update=upd,
            geometry={
                "topology_type": "feedforward",
                "depth": depth,
                "hidden_dim": hidden,
            },
            input_dim=input_dim,
            output_dim=output_dim,
        )

    return train_task(factory, "spiral", 1, batch_size=64, device="cpu", seed=42)[-1]


def main() -> None:
    for dyn, credit, upd, depth, hidden in CASES:
        final = probe(dyn, credit, upd, depth, hidden)
        print(
            f"{dyn}|{credit}|{upd}|depth={depth}|hidden={hidden} "
            f"loss={final.get('train_loss')} acc={final.get('train_acc')}"
        )
        for name, value in final.items():
            if isinstance(value, float) and not math.isfinite(value):
                print(f"  non-finite metric: {name}={value}")


if __name__ == "__main__":
    main()
