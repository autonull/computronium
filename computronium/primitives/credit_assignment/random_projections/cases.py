"""Deterministic test cases for Random Projections Credit.

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
    activations: list[torch.Tensor]
    nudged_activations: list[torch.Tensor]
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

    # Create activations with requires_grad for autograd path
    h1 = torch.randn(
        batch,
        width,
        device=device,
        dtype=dtype,
        generator=generator,
        requires_grad=True,
    )
    h2 = torch.randn(
        batch,
        width,
        device=device,
        dtype=dtype,
        generator=generator,
        requires_grad=True,
    )

    activations = [state, h1, h2]

    # Nudged activations also need requires_grad
    h1_n = torch.randn(
        batch,
        width,
        device=device,
        dtype=dtype,
        generator=generator,
        requires_grad=True,
    )
    h2_n = torch.randn(
        batch,
        width,
        device=device,
        dtype=dtype,
        generator=generator,
        requires_grad=True,
    )
    nudged_activations = [state, h1_n, h2_n]

    # Create a fixed geometry for deterministic testing
    # Save/restore RNG state to ensure deterministic geometry creation
    rng_state = torch.get_rng_state()
    torch.manual_seed(seed)
    try:
        geometry = FeedforwardGeometry(
            GeometryConfig.feedforward(
                input_dim=width, output_dim=width, hidden_dims=(width,)
            )
        ).to(device)
    finally:
        torch.set_rng_state(rng_state)

    config = {
        "feedback_scale": 0.1,
        "seed": seed,
    }

    return Case(
        state=state,
        activations=activations,
        nudged_activations=nudged_activations,
        config=config,
        geometry=geometry,
    )
