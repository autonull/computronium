"""Deterministic test cases for Null Plasticity.

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
    psi: dict[str, torch.Tensor]


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

    # Null plasticity has no plastic state
    psi = {}

    config = {
        "seed": seed,
    }

    return Case(
        state=state,
        prediction=prediction,
        multiplier=multiplier,
        config=config,
        psi=psi,
    )
