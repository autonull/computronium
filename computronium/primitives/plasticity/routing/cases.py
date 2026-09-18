"""Deterministic test cases for Routing Plasticity.

These cases are intentionally small. They are used for parity tests,
smoke tests, and microbenchmarks. They are not scientific benchmarks.
"""

from dataclasses import dataclass
from typing import Any

import torch


@dataclass(frozen=True, slots=True)
class Case:
    gate_logits: torch.Tensor
    active_routes: torch.Tensor
    pre_activity: torch.Tensor
    config: dict[str, Any]


def make_case(
    *,
    device: str = "cpu",
    dtype: torch.dtype = torch.float32,
    seed: int = 0,
) -> Case:
    generator = torch.Generator(device=device).manual_seed(seed)

    # Batch size 2, gate_dim 8, input_dim 16
    batch_size = 2
    gate_dim = 8
    input_dim = 16

    # Initial gate logits and active routes (zeros)
    gate_logits = torch.zeros(batch_size, gate_dim, device=device, dtype=dtype)
    active_routes = torch.zeros(batch_size, gate_dim, device=device, dtype=dtype)

    # Pre activity (input)
    pre_activity = torch.randn(
        batch_size, input_dim, device=device, dtype=dtype, generator=generator
    )

    config = {
        "gate_dim": gate_dim,
        "temperature": 1.0,
        "top_k": None,
        "decay": 0.99,
        "learning_rate": 0.01,
        "seed": seed,
    }

    return Case(
        gate_logits=gate_logits,
        active_routes=active_routes,
        pre_activity=pre_activity,
        config=config,
    )
