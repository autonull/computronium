"""Deterministic test cases for Local Goodness Credit Assignment.

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
    local_objective: str = "ff",
    scale: int = 1,
):
    batch, width = 2 * scale, 4 * scale

    config = {
        "local_objective": local_objective,
        "feedback_scale": 1.0,
        "orthogonal_init": True,
        "readout_error": False,
        "credit_norm": "rms",
        "learned_feedback": False,
        "feedback_lr": 0.01,
        "feedback_update_every": 10,
        "target": None,  # Will be set by make_primitive_case
    }

    return make_primitive_case(
        geometry_factory=lambda: FeedforwardGeometry(
            GeometryConfig.feedforward(
                input_dim=width,
                output_dim=width,
                hidden_dims=(width, width),
            )
        ),
        config=config,
        device=device,
        dtype=dtype,
        seed=seed,
        batch=batch,
        width=width,
        requires_grad=True,
    )
