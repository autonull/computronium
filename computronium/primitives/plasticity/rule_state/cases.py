"""Deterministic test cases for Rule State Plasticity.

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

    # Rule state plasticity has operator_logits and controller_state
    psi = {
        "operator_logits": torch.zeros(2, 4, device=device, dtype=dtype),
        "controller_state": torch.zeros(2, 16, device=device, dtype=dtype),
    }

    config = {
        "num_operators": 4,
        "operator_dim": 8,
        "controller_hidden": 16,
        "temperature": 1.0,
        "learning_rate": 0.01,
        "decay": 0.99,
        "consolidation_config": {},
        "seed": seed,
    }

    return Case(
        state=state,
        prediction=prediction,
        multiplier=multiplier,
        config=config,
        psi=psi,
    )
