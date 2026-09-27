"""Deterministic test cases for Local Goodness Credit Assignment.

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
    local_objective: str = "ff",
    scale: int = 1,
) -> Case:
    generator = torch.Generator(device=device).manual_seed(seed)

    batch, width = 2 * scale, 4 * scale

    # Create geometry with deterministic weights
    rng_state = torch.get_rng_state()
    torch.manual_seed(seed)
    try:
        geometry = FeedforwardGeometry(
            GeometryConfig.feedforward(
                input_dim=width,
                output_dim=width,
                hidden_dims=(width, width),
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

    # Run forward pass for free activations with requires_grad for FF mode
    free_input = torch.randn(
        batch,
        width,
        device=device,
        dtype=dtype,
        generator=generator,
        requires_grad=True,
    )
    free_activations = [free_input]
    x = free_input
    for layer in geometry._layers:
        x = layer(x)
        free_activations.append(x)

    # Run forward pass for nudged activations with requires_grad
    nudged_gen = torch.Generator(device=device).manual_seed(seed + 1)
    nudged_input = torch.randn(
        batch,
        width,
        device=device,
        dtype=dtype,
        generator=nudged_gen,
        requires_grad=True,
    )
    nudged_activations = [nudged_input]
    x_n = nudged_input
    for layer in geometry._layers:
        x_n = layer(x_n)
        nudged_activations.append(x_n)

    config = {
        "local_objective": local_objective,
        "feedback_scale": 1.0,
        "orthogonal_init": True,
        "readout_error": False,
        "credit_norm": "rms",
        "learned_feedback": False,
        "feedback_lr": 0.01,
        "feedback_update_every": 10,
        "target": torch.randint(0, width, (batch,), device=device),
        "seed": seed,
    }

    return Case(
        weights=weights,
        free_activations=free_activations,
        nudged_activations=nudged_activations,
        config=config,
        geometry=geometry,
    )
