"""Deterministic test cases for Temporal Trace Credit (STDP).

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
        "steps": 3,
        "a_plus": 1.0,
        "a_minus": 0.5,
        "tau": 20.0,
        "tau_pre": 0.9,
        "tau_post": 0.9,
        "target": torch.randint(0, 4, (2,), device=device, generator=generator),
    }

    return Case(
        state=state,
        prediction=prediction,
        multiplier=multiplier,
        config=config,
    )
