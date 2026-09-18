"""Deterministic test cases for Local Goodness Credit Assignment.

These cases are intentionally small. They are used for parity tests,
smoke tests, and microbenchmarks. They are not scientific benchmarks.
"""

from dataclasses import dataclass
from typing import Any

import torch


@dataclass(frozen=True, slots=True)
class Case:
    weights: list[torch.Tensor]
    free_activations: list[torch.Tensor]
    nudged_activations: list[torch.Tensor]
    config: dict[str, Any]


def make_case(
    *,
    device: str = "cpu",
    dtype: torch.dtype = torch.float32,
    seed: int = 0,
    local_objective: str = "ff",
) -> Case:
    generator = torch.Generator(device=device).manual_seed(seed)

    # Create weight matrices for a 3-layer network (784 -> 256 -> 128 -> 10)
    # For testing, use smaller dims
    weight_shapes = [
        (4, 4),  # layer 0: 4 -> 4
        (4, 4),  # layer 1: 4 -> 4
        (4, 4),  # layer 2: 4 -> 4
    ]
    weights = [
        torch.randn(out_dim, in_dim, device=device, dtype=dtype, generator=generator)
        for out_dim, in_dim in weight_shapes
    ]

    # Free activations: [input, h1, h2, output]
    free_activations = [
        torch.randn(2, 4, device=device, dtype=dtype, generator=generator)
        for _ in range(4)
    ]

    # Nudged activations: slightly different, with requires_grad for FF mode
    nudged_gen = torch.Generator(device=device).manual_seed(seed + 1)
    nudged_activations = [
        torch.randn(
            2, 4, device=device, dtype=dtype, generator=nudged_gen, requires_grad=True
        )
        for _ in range(4)
    ]

    config = {
        "local_objective": local_objective,
        "feedback_scale": 1.0,
        "orthogonal_init": True,
        "readout_error": False,
        "credit_norm": "rms",
        "learned_feedback": False,
        "feedback_lr": 0.01,
        "feedback_update_every": 10,
        "target": torch.randint(0, 4, (2,), device=device),
        "seed": seed,
    }

    return Case(
        weights=weights,
        free_activations=free_activations,
        nudged_activations=nudged_activations,
        config=config,
    )
