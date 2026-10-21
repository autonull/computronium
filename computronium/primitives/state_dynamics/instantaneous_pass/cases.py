"""Deterministic test cases for Instantaneous Pass.

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
) -> DynamicsCase:
    """Build the deterministic case this dynamics' steps consume."""
    return make_dynamics_case(
        geometry_factory=lambda: FeedforwardGeometry(
            GeometryConfig.feedforward(input_dim=4, output_dim=4, hidden_dims=())
        ),
        config={
            "steps": 3,
            "step_size": 0.1,
            "target": None,
        },
        device=device,
        dtype=dtype,
        seed=seed,
    )
