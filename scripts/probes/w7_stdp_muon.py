"""W7 Blitz cell — plain STDP × Muon 0.02 (TODO15 §2.1).

TemporalTraceCredit STDP never saw a Muon-class optimizer (the existing
probe, scripts/probes/spiking_learning.py, hardcodes EuclideanUpdate lr
0.2; prior verdict 0.048 train acc = chance). One cell, pre-registered:
train_acc ≥ 0.50 → Reopened; < 0.30 → Boundary.

uv run python scripts/probes/w7_stdp_muon.py
Walltime printed, never recorded.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

import torch

sys.path.insert(0, str(Path(__file__).resolve().parent))

from spiking_learning import BATCH_CAP, DEPTHS, SETTLE_STEPS, WIDTH, _flatten

from computronium import (  # type: ignore[attr-defined]
    CreditAssignmentConfig,
    DigitalSubstrate,
    FeedforwardGeometry,
    GeometryConfig,
    ParameterUpdateConfig,
    RiemannianOrthogonalUpdate,
    SpikeIntegrationDynamics,
    StateDynamicsConfig,
    SubstrateConfig,
    SystemTrainer,
    SystemTrainerConfig,
    TemporalTraceCredit,
    compose_system,
    create_task,
)

LR = 0.02


def _build_muon(depth: int):
    torch.manual_seed(0)
    return compose_system(
        substrate=DigitalSubstrate(SubstrateConfig.digital(device="cpu")),
        geometry=FeedforwardGeometry(
            GeometryConfig.feedforward(
                input_dim=784,
                output_dim=10,
                hidden_dims=(WIDTH,) * depth,
            )
        ),
        dynamics=SpikeIntegrationDynamics(
            StateDynamicsConfig.spike_integration(max_steps=SETTLE_STEPS)
        ),
        credit=TemporalTraceCredit(CreditAssignmentConfig.temporal_trace()),
        update=RiemannianOrthogonalUpdate(
            ParameterUpdateConfig.riemannian_orthogonal(step_size=LR)
        ),
    )


def main() -> int:
    t0 = time.time()
    task = create_task("mnist", device="cpu", quick_mode=True, num_workers=0)
    task.setup()
    config = SystemTrainerConfig(max_epochs=1, device="cpu", seed=42)
    torch.manual_seed(0)
    train_data = list(_flatten(task.get_dataloader("train"), BATCH_CAP))

    for depth in DEPTHS:
        system = _build_muon(depth)
        metrics = SystemTrainer(
            system=system, config=config, train_data=train_data
        ).fit()[-1]
        print(
            f"STDP x muon {LR} depth {depth}: train_acc {metrics['train_acc']:.3f}",
            flush=True,
        )

    print(f"walltime {time.time() - t0:.1f}s (printed, never recorded)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
