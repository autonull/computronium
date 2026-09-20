"""Deterministic test cases for Natural Gradient.

These cases are intentionally small. They are used for parity tests,
smoke tests, and microbenchmarks. They are not scientific benchmarks.
"""

from dataclasses import dataclass
from typing import Any

import torch


@dataclass(frozen=True, slots=True)
class Case:
    state: torch.Tensor
    prediction: torch.Tensor
    multiplier: torch.Tensor
    config: dict[str, Any]


def make_case(
    *,
    device: str = "cpu",
    dtype: torch.dtype = torch.float32,
    seed: int = 0,
) -> Case:
    generator = torch.Generator(device=device).manual_seed(seed)

    # Input batch of 2, feature dim 4
    state = torch.randn(2, 4, device=device, dtype=dtype, generator=generator)
    prediction = torch.randn(2, 4, device=device, dtype=dtype, generator=generator)
    multiplier = torch.randn(2, 4, device=device, dtype=dtype, generator=generator)

    config = {
        "step_size": 1e-3,
        "momentum": 0.9,
        "fisher_damping": 1e-3,
        "beta2": 0.999,
        "eps": 1e-8,
        "grad_clip": 1.0,
        "seed": seed,
    }

    return Case(
        state=state,
        prediction=prediction,
        multiplier=multiplier,
        config=config,
    )
