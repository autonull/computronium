"""Deterministic test cases for Reverse Mode.

These cases are intentionally small. They are used for parity tests,
smoke tests, and microbenchmarks. They are not scientific benchmarks.
"""

from dataclasses import dataclass
from typing import Any

import torch

from computronium.harness import seeded_rng
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
) -> Case:
    generator = torch.Generator(device=device).manual_seed(seed)

    # Create geometry with proper weights
    # Save/restore RNG state to ensure deterministic geometry creation
    with seeded_rng(seed):
        geometry = FeedforwardGeometry(
            GeometryConfig.feedforward(input_dim=4, output_dim=4, hidden_dims=(4,))
        )

    # Run forward pass to get activations with proper gradient connections
    state = torch.randn(
        2, 4, device=device, dtype=dtype, generator=generator, requires_grad=True
    )
    activations = [state]
    x = state
    for layer in geometry._layers:
        x = layer(x)
        activations.append(x)

    # Nudged activations - also run forward with requires_grad
    with seeded_rng(seed + 1000):
        state_n = torch.randn(
            2, 4, device=device, dtype=dtype, generator=generator, requires_grad=True
        )
        nudged_activations = [state_n]
        x_n = state_n
        for layer in geometry._layers:
            x_n = layer(x_n)
            nudged_activations.append(x_n)

    config = {
        "beta": 0.5,
        "seed": seed,
    }

    return Case(
        state=state,
        activations=activations,
        nudged_activations=nudged_activations,
        config=config,
        geometry=geometry,
    )
