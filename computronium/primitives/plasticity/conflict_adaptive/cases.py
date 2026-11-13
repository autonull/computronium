"""Deterministic test cases for Conflict-Adaptive Plasticity.

These cases are intentionally small. They are used for parity tests,
smoke tests, and microbenchmarks. They are not scientific benchmarks.
"""

from dataclasses import dataclass
from typing import Any

import torch


@dataclass(frozen=True, slots=True)
class Case:
    psi: dict[str, torch.Tensor]
    pre_activity: torch.Tensor
    target: torch.Tensor
    post_activity: torch.Tensor
    config: dict[str, Any]


def make_case(
    *,
    device: str = "cpu",
    dtype: torch.dtype = torch.float32,
    seed: int = 0,
) -> Case:
    generator = torch.Generator(device=device).manual_seed(seed)

    batch_size = 2
    hidden_dim = 16
    num_classes = 4

    psi: dict[str, torch.Tensor] = {}
    pre_activity = torch.randn(
        batch_size, hidden_dim, device=device, dtype=dtype, generator=generator
    )
    target = torch.randint(
        0, num_classes, (batch_size,), device=device, generator=generator
    )
    post_activity = torch.randn(
        batch_size, num_classes, device=device, dtype=dtype, generator=generator
    )

    config = {
        "conflict_threshold": 0.65,
        "forget_decay": 0.5,
        "ridge_lambda": 1e-3,
        "replace_readout": True,
        "seed": seed,
    }

    return Case(
        psi=psi,
        pre_activity=pre_activity,
        target=target,
        post_activity=post_activity,
        config=config,
    )
