"""Deterministic test cases for Muon (Riemannian Orthogonal Update).

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

    state = torch.randn(2, 4, device=device, dtype=dtype, generator=generator)
    prediction = torch.randn(2, 4, device=device, dtype=dtype, generator=generator)
    multiplier = torch.randn(2, 4, device=device, dtype=dtype, generator=generator)

    config = {
        "steps": 1,
        "step_size": 0.01,
        "momentum": 0.9,
        "ortho_steps": 0,
        "seed": seed,
    }

    return Case(
        state=state,
        prediction=prediction,
        multiplier=multiplier,
        config=config,
    )
