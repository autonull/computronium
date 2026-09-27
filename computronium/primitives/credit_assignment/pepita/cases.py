"""Deterministic test cases for PEPITA Credit Assignment.

These cases are intentionally small. They are used for parity tests,
smoke tests, and microbenchmarks. They are not scientific benchmarks.
"""

from dataclasses import dataclass
from typing import Any

import torch

from computronium.ontology.geometry import FeedforwardGeometry, GeometryConfig


@dataclass(frozen=True, slots=True)
class Case:
    weights: list[torch.Tensor]
    free_activations: list[torch.Tensor]
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

    # Create geometry with deterministic weights
    rng_state = torch.get_rng_state()
    torch.manual_seed(seed)
    try:
        geometry = FeedforwardGeometry(
            GeometryConfig.feedforward(
                input_dim=4,
                output_dim=4,
                hidden_dims=(8,),
            )
        )
    finally:
        torch.set_rng_state(rng_state)

    # Extract weights for reference (only Linear layers)
    weights = [
        layer.weight.data.clone()
        for layer in geometry._layers
        if isinstance(layer, torch.nn.Linear)
    ]

    # Run forward pass for free activations
    free_input = torch.randn(2, 4, device=device, dtype=dtype, generator=generator)
    free_activations = [free_input]
    x = free_input
    for layer in geometry._layers:
        x = layer(x)
        free_activations.append(x)

    # Run forward pass for nudged activations
    nudged_gen = torch.Generator(device=device).manual_seed(seed + 1)
    nudged_input = torch.randn(2, 4, device=device, dtype=dtype, generator=nudged_gen)
    nudged_activations = [nudged_input]
    x_n = nudged_input
    for layer in geometry._layers:
        x_n = layer(x_n)
        nudged_activations.append(x_n)

    config = {
        "gamma": 0.05,
        "feedback_matrix": torch.randn(
            4, 4, device=device, dtype=dtype, generator=generator
        ),
        "target": torch.randint(0, 4, (2,), device=device, generator=generator),
        "seed": seed,
    }

    return Case(
        weights=weights,
        free_activations=free_activations,
        nudged_activations=nudged_activations,
        config=config,
        geometry=geometry,
    )
