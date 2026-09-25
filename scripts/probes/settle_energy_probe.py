"""Diagnose EnergyMinimizationDynamics settling on RecurrentGeometry.

Informed the fix for the 4 failing settling/thermo tests
(tests/unit/core/test_dynamics.py::TestEnergyMinimizationDynamics and
tests/unit/core/test_credit.py::TestSettlingConvergence): print the free-energy
trace, the output delta that drives early stopping, and the geometry's param
layout so the layered-vs-recurrent mismatch is visible.
"""

from __future__ import annotations

import torch

from computronium.ontology import (
    DigitalSubstrate,
    EnergyMinimizationDynamics,
    GeometryConfig,
    RecurrentGeometry,
    StateDynamicsConfig,
    SubstrateConfig,
    SystemState,
)
from computronium.ontology._settle_kernel import extract_layered_params


def main() -> None:
    device = torch.device("cpu")
    torch.manual_seed(3)
    geometry = RecurrentGeometry(
        GeometryConfig.recurrent(
            input_dim=784, output_dim=10, hidden_dims=(256,), init_scale=0.1
        ),
        hidden_dim=256,
    ).to(device)
    substrate = DigitalSubstrate(SubstrateConfig.digital(device=str(device)))

    print("param keys:", sorted(geometry.params))
    for k, v in geometry.params.items():
        print(f"  {k}: {tuple(v.shape)}")
    layered = extract_layered_params(geometry)
    print("extract_layered_params ->", None if layered is None else "LayeredParams")
    if layered is not None:
        print("  weights:", [tuple(w.shape) for w in layered.weights])
        print(
            "  biases:", [None if b is None else tuple(b.shape) for b in layered.biases]
        )
        print(
            "  activations:",
            [None if a is None else str(a) for a in layered.activations],
        )
        print("  residual:", layered.residual)

    x = torch.randn(4, 784, device=device)
    y = torch.randint(0, 10, (4,), device=device)

    acts = geometry.forward_with_intermediates(x, substrate)
    print("\nforward_with_intermediates ->", [tuple(a.shape) for a in acts])
    if hasattr(geometry, "settle_blocks"):
        print("has settle_blocks:", callable(geometry.settle_blocks))

    dynamics = EnergyMinimizationDynamics(
        StateDynamicsConfig.energy_minimization(
            max_steps=500,
            convergence_threshold=1e-4,
            convergence_start=10,
            step_size=0.01,
            beta=0.5,
            momentum=0.0,
            track_free_energy_per_iter=True,
            gradient_checkpointing=False,
        )
    )
    state = SystemState(x=x, y=y)
    state.activations = list(acts)
    out = dynamics.settle(state, geometry, substrate, target=None)

    hist = dynamics.get_free_energy_history() or []
    print("\nhistory len:", len(hist))
    if hist:
        print("first 5:", [f"{v:.6e}" for v in hist[:5]])
        print("last 5:", [f"{v:.6e}" for v in hist[-5:]])
        print("delta first/last:", abs(hist[1] - hist[0]), abs(hist[-1] - hist[-2]))
        print("min/max:", min(hist), max(hist))
        nonmono = sum(1 for a, b in zip(hist, hist[1:], strict=False) if b > a)
        print("rising steps:", nonmono, "of", len(hist) - 1)
    print("settle_steps_used:", dynamics._settle_steps_used)
    print("free_state shapes:", [tuple(a.shape) for a in (out.free_state or [])])


if __name__ == "__main__":
    main()
