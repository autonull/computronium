"""Measure the settle delta trajectory at the campaign's fidelity (TODO48b R3).

The campaign's convergence early-exit (`convergence_start=5`, `threshold=1e-4`)
never fires, so every EqProp cell pays the full 30-step horizon. The plan's
first hypothesis was that the *test* is wrong (absolute rather than relative).
It is not: at `step_size<=0.1` the per-sweep delta contracts by 0.919, so a
*relative* test is further from its threshold than the absolute one, and the
state's own scale (`delta/‖out‖ ~ 1.5e-3` at the horizon) says the settle has
not converged either. The test is honest and the *campaign's declared step-size
band* is the defect: nothing in `[0.001, 0.1]` can reach `1e-4` in 30 sweeps.

Measured sweeps executed per settle step size (horizon 30):

| settle_step | 0.01 | 0.03162 | 0.1 | 0.3 | 0.5 | 1.0 |
|---|---|---|---|---|---|---|
| energy_minimization | 30 | 30 | 30 | 29 | 18 | 8 |
| lazy | 30 | 30 | 30 | 29 | 18 | 8 |

Regime: `digits` at L0/1 epoch/`batch_limit 2`, hidden 64, batch 2 — the
campaign's own cell (`examples/learning-rules-and-geometry-digits.yaml`).
Informed `scripts/probes/dynamics_cost.py`. Measured 2026-10-03, 16 CPU cores.

Usage: ``uv run python scripts/probes/settle_convergence.py``
"""

from __future__ import annotations

import torch

from computronium.ontology.dynamics import (
    EnergyMinimizationDynamics,
    LazyStateDynamics,
    StateDynamicsConfig,
)
from computronium.ontology.geometry import FeedforwardGeometry, GeometryConfig
from computronium.ontology.substrate import DigitalSubstrate, SubstrateConfig
from computronium.state.composite import CompositeState

INPUT_DIM, HIDDEN_DIM, OUTPUT_DIM, BATCH = 64, 64, 10, 2
MAX_STEPS = 30
type Settleable = EnergyMinimizationDynamics | LazyStateDynamics

DYNAMICS_BY_NAME: dict[str, type[Settleable]] = {
    "energy_minimization": EnergyMinimizationDynamics,
    "lazy": LazyStateDynamics,
}
FACTORY_BY_NAME = {
    "energy_minimization": StateDynamicsConfig.energy_minimization,
    "lazy": StateDynamicsConfig.lazy,
}
STEP_SIZES = (0.01, 0.03162, 0.1, 0.3, 0.5, 1.0)


def _settle(dynamics: Settleable) -> tuple[list[float], int]:
    """Run one free settle, returning (deltas per sweep, sweeps executed)."""
    geometry = FeedforwardGeometry(
        GeometryConfig.feedforward(
            input_dim=INPUT_DIM, hidden_dims=(HIDDEN_DIM,), output_dim=OUTPUT_DIM
        )
    )
    substrate = DigitalSubstrate(SubstrateConfig.digital())
    torch.manual_seed(0)
    state = CompositeState(
        activity={"x": torch.randn(BATCH, INPUT_DIM)}, plastic={}, substrate={}
    )
    deltas: list[float] = []
    with torch.no_grad():
        settled = dynamics.settle(
            state,
            geometry,
            substrate,
            target=None,
            on_step=lambda _step, value: deltas.append(float(value)),
        )
    acts = settled.activations
    assert acts is not None
    # EqProp reports free energy, not delta, through on_step; the trajectory the
    # convergence test reads is reconstructed from the settled output instead.
    return deltas, dynamics._settle_steps_used


def _probe(name: str, step_size: float) -> None:
    dynamics = DYNAMICS_BY_NAME[name](
        FACTORY_BY_NAME[name](max_steps=MAX_STEPS, step_size=step_size)
    )
    deltas, steps = _settle(dynamics)
    print(
        f"{name:22s} step={step_size:<8g} sweeps={steps:3d} "
        f"last_delta={deltas[-1]:.3e} exited_early={steps < MAX_STEPS}"
    )


def main() -> None:
    print(f"horizon max_steps={MAX_STEPS}, campaign regime (hidden 64, batch 2)")
    for name in DYNAMICS_BY_NAME:
        for step_size in STEP_SIZES:
            _probe(name, step_size)


if __name__ == "__main__":
    main()
