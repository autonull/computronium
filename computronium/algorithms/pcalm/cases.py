"""Deterministic test cases for PC-ALM algorithm.

These cases are intentionally small. They are used for parity tests,
smoke tests, and microbenchmarks. They are not scientific benchmarks.
"""

import torch

from computronium.harness import AlgorithmCase, make_algorithm_case
from computronium.ontology.geometry import FeedforwardGeometry, GeometryConfig

Case = AlgorithmCase


def make_case(
    *,
    device: str = "cpu",
    dtype: torch.dtype = torch.float32,
    seed: int = 0,
    scale: int = 1,
) -> AlgorithmCase:
    """Build the deterministic case this algorithm's steps consume."""
    width = 4 * scale
    return make_algorithm_case(
        geometry_factory=lambda: FeedforwardGeometry(
            GeometryConfig.feedforward(
                input_dim=width, output_dim=width, hidden_dims=()
            )
        ).to(device),
        config={
            "steps": 3,
            "step_size": 0.1,
            "rho": 1.0,
            "beta": 0.5,
            "prospective_leak": 0.0,
            "tol": 1e-4,
            "lr": 1e-3,
        },
        device=device,
        dtype=dtype,
        seed=seed,
        batch=2 * scale,
        width=width,
    )
