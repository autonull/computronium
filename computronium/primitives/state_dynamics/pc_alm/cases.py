"""Deterministic test cases for PC-ALM settling.

These cases are intentionally small. They are used for parity tests,
smoke tests, and microbenchmarks. They are not scientific benchmarks.
"""

import torch

from computronium.harness import DynamicsCase, make_dynamics_case
from computronium.ontology.geometry import FeedforwardGeometry, GeometryConfig

Case = DynamicsCase


def make_case(
    *,
    device: str = "cpu",
    dtype: torch.dtype = torch.float32,
    seed: int = 0,
    scale: int = 1,
) -> DynamicsCase:
    """Build the deterministic case this dynamics' steps consume."""
    width = 4 * scale

    def _geometry() -> FeedforwardGeometry:
        return FeedforwardGeometry(
            GeometryConfig.feedforward(
                input_dim=width, output_dim=width, hidden_dims=()
            )
        ).to(device)

    return make_dynamics_case(
        geometry_factory=_geometry,
        config={
            "steps": 3,
            "step_size": 0.1,
            "rho": 1.0,
            "beta": 0.5,
            "prospective_leak": 0.0,
            "tol": 1e-4,
            "target": None,
        },
        device=device,
        dtype=dtype,
        seed=seed,
        batch=2 * scale,
        width=4 * scale,
    )
