"""Deterministic test cases for MomentumEqprop algorithm.

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
) -> AlgorithmCase:
    """Build the deterministic case this algorithm's steps consume."""
    return make_algorithm_case(
        geometry_factory=lambda: FeedforwardGeometry(
            GeometryConfig.feedforward(input_dim=4, output_dim=4, hidden_dims=())
        ),
        config={
            "lr": 1e-3,
        },
        device=device,
        dtype=dtype,
        seed=seed,
    )
