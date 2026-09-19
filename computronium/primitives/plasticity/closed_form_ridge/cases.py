"""Deterministic test cases for Closed-form Ridge Plasticity.

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


class _MockContext:
    """Minimal mock context for testing - only needs device property."""

    def __init__(self, device: torch.device):
        self._device = device

    @property
    def device(self) -> torch.device:
        return self._device


def make_case(
    *,
    device: str = "cpu",
    dtype: torch.dtype = torch.float32,
    seed: int = 0,
) -> Case:
    generator = torch.Generator(device=device).manual_seed(seed)

    # Batch size 2, hidden_dim 16, num_classes 4
    batch_size = 2
    hidden_dim = 16
    num_classes = 4

    # Initial psi state (empty - will be populated by step)
    psi = {}

    # Pre-readout settled activity (hidden layer)
    pre_activity = torch.randn(
        batch_size, hidden_dim, device=device, dtype=dtype, generator=generator
    )

    # Target class indices
    target = torch.randint(
        0, num_classes, (batch_size,), device=device, generator=generator
    )

    # Post-readout activity (logits)
    post_activity = torch.randn(
        batch_size, num_classes, device=device, dtype=dtype, generator=generator
    )

    config = {
        "ridge_lambda": 1e-3,
        "seed": seed,
    }

    return Case(
        psi=psi,
        pre_activity=pre_activity,
        target=target,
        post_activity=post_activity,
        config=config,
    )
