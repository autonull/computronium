"""Deterministic test cases for PC-ALM settling.

These cases are intentionally small. They are used for parity tests,
smoke tests, and microbenchmarks. They are not scientific benchmarks.
"""

from dataclasses import dataclass
from typing import Any

import torch

from computronium.ontology.geometry import FeedforwardGeometry, GeometryConfig


@dataclass(frozen=True, slots=True)
class Case:
    state: torch.Tensor
    prediction: torch.Tensor
    multiplier: torch.Tensor
    config: dict[str, Any]
    geometry: FeedforwardGeometry


def make_case(
    *,
    device: str = "cpu",
    dtype: torch.dtype = torch.float32,
    seed: int = 0,
    scale: int = 1,
) -> Case:
    generator = torch.Generator(device=device).manual_seed(seed)

    batch, width = 2 * scale, 4 * scale
    state = torch.randn(batch, width, device=device, dtype=dtype, generator=generator)
    prediction = torch.randn(
        batch, width, device=device, dtype=dtype, generator=generator
    )
    multiplier = torch.randn(
        batch, width, device=device, dtype=dtype, generator=generator
    )

    # Create a fixed geometry for deterministic testing
    # Save/restore RNG state to ensure deterministic geometry creation
    rng_state = torch.get_rng_state()
    torch.manual_seed(seed)
    try:
        geometry = FeedforwardGeometry(
            GeometryConfig.feedforward(
                input_dim=width, output_dim=width, hidden_dims=()
            )
        ).to(device)
    finally:
        torch.set_rng_state(rng_state)

    config = {
        "steps": 3,
        "step_size": 0.1,
        "rho": 1.0,
        "beta": 0.5,
        "prospective_leak": 0.0,
        "tol": 1e-4,
        "target": None,
        "seed": seed,
    }

    return Case(
        state=state,
        prediction=prediction,
        multiplier=multiplier,
        config=config,
        geometry=geometry,
    )
