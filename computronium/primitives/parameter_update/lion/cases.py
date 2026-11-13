"""Deterministic test cases for Lion Update.

These cases are intentionally small. They are used for parity tests,
smoke tests, and microbenchmarks. They are not scientific benchmarks.
"""

import torch

from computronium.harness import UpdateCase, make_update_case

Case = UpdateCase


def make_case(
    *,
    device: str = "cpu",
    dtype: torch.dtype = torch.float32,
    seed: int = 0,
) -> UpdateCase:
    """Build the deterministic case this update's steps consume."""
    return make_update_case(
        config={
            "step_size": 0.001,
            "momentum": 0.9,
            "beta2": 0.99,
            "grad_clip": 1.0,
        },
        device=device,
        dtype=dtype,
        seed=seed,
    )
