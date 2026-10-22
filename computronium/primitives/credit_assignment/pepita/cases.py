"""Deterministic test cases for PEPITA Credit Assignment.

These cases are intentionally small. They are used for parity tests,
smoke tests, and microbenchmarks. They are not scientific benchmarks.
"""

import torch

from computronium.ontology.geometry import FeedforwardGeometry, GeometryConfig
from computronium.primitives._common import make_primitive_case


def make_case(
    *,
    device: str = "cpu",
    dtype: torch.dtype = torch.float32,
    seed: int = 0,
):
    generator = torch.Generator(device=device).manual_seed(seed)
    config = {
        "gamma": 0.05,
        "feedback_matrix": torch.randn(
            4, 4, device=device, dtype=dtype, generator=generator
        ),
        "target": torch.randint(0, 4, (2,), device=device, generator=generator),
        "seed": seed,
    }

    return make_primitive_case(
        geometry_factory=lambda: FeedforwardGeometry(
            GeometryConfig.feedforward(
                input_dim=4,
                output_dim=4,
                hidden_dims=(8,),
            )
        ),
        config=config,
        device=device,
        dtype=dtype,
        seed=seed,
        batch=2,
        width=4,
        requires_grad=True,
    )
