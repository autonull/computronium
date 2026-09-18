"""Deterministic test cases for Fast Weight Plasticity.

These cases are intentionally small. They are used for parity tests,
smoke tests, and microbenchmarks. They are not scientific benchmarks.
"""

from dataclasses import dataclass
from typing import Any

import torch


@dataclass(frozen=True, slots=True)
class Case:
    fast_weights: torch.Tensor
    pre_activity: torch.Tensor
    post_activity: torch.Tensor
    config: dict[str, Any]


def make_case(
    *,
    device: str = "cpu",
    dtype: torch.dtype = torch.float32,
    seed: int = 0,
) -> Case:
    generator = torch.Generator(device=device).manual_seed(seed)

    # Batch size 2, fast_weight_dim 16, input_dim 8, output_dim 4
    batch_size = 2
    fast_weight_dim = 16
    input_dim = 8
    output_dim = 4

    # Initial fast weights (zeros)
    fast_weights = torch.zeros(batch_size, fast_weight_dim, device=device, dtype=dtype)

    # Pre and post activities (settled activities)
    pre_activity = torch.randn(
        batch_size, input_dim, device=device, dtype=dtype, generator=generator
    )
    post_activity = torch.randn(
        batch_size, output_dim, device=device, dtype=dtype, generator=generator
    )

    config = {
        "fast_weight_dim": fast_weight_dim,
        "decay": 0.9,
        "learning_rate": 0.1,
        "outer_product_scale": 1.0,
        "step": 0,
        "seed": seed,
    }

    return Case(
        fast_weights=fast_weights,
        pre_activity=pre_activity,
        post_activity=post_activity,
        config=config,
    )
