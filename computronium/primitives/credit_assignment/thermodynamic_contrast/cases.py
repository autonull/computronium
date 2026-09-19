"""Deterministic test cases for Thermodynamic Contrast Credit.

These cases are intentionally small. They are used for parity tests,
smoke tests, and microbenchmarks. They are not scientific benchmarks.
"""

from dataclasses import dataclass
from typing import Any

import torch
from torch import nn

from computronium.ontology.geometry import FeedforwardGeometry, GeometryConfig


@dataclass(frozen=True, slots=True)
class Case:
    state: torch.Tensor
    prediction: torch.Tensor
    multiplier: torch.Tensor
    config: dict[str, Any]
    free_activations: list[torch.Tensor]
    nudged_activations: list[torch.Tensor]
    weights: list[torch.Tensor]
    geometry: FeedforwardGeometry


def _make_activations(
    x: torch.Tensor,
    weight_shapes: list[tuple[int, int]],
    seed: int,
) -> list[torch.Tensor]:
    """Create a list of deterministic activations from input through layers."""
    generator = torch.Generator(device=x.device).manual_seed(seed)
    acts = [x]
    for i, (out_dim, in_dim) in enumerate(weight_shapes):
        # Deterministic linear transformation
        w = torch.randn(
            out_dim, in_dim, device=x.device, dtype=x.dtype, generator=generator
        )
        acts.append(acts[-1] @ w.T)
    return acts


def _make_weights(
    weight_shapes: list[tuple[int, int]],
    seed: int,
    device: str,
    dtype: torch.dtype,
) -> list[torch.Tensor]:
    """Create deterministic weights."""
    generator = torch.Generator(device=device).manual_seed(seed + 1000)
    weights = []
    for out_dim, in_dim in weight_shapes:
        w = torch.randn(
            out_dim, in_dim, device=device, dtype=dtype, generator=generator
        )
        weights.append(w)
    return weights


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

    # 2-layer network: 4 -> 4 -> 4
    weight_shapes = [(4, 4), (4, 4)]
    weights = _make_weights(weight_shapes, seed, device, dtype)

    # Create free and nudged activations
    free_acts = _make_activations(state, weight_shapes, seed)
    nudged_acts = _make_activations(prediction, weight_shapes, seed + 1)

    # Create a fixed geometry for deterministic testing
    rng_state = torch.get_rng_state()
    torch.manual_seed(seed)
    try:
        layers = []
        for i, (out_dim, in_dim) in enumerate(weight_shapes):
            layer = nn.Linear(in_dim, out_dim, bias=False)
            layer.weight.data = weights[i].clone()
            layers.append(layer)

        geometry = FeedforwardGeometry(
            GeometryConfig.feedforward(input_dim=4, output_dim=4, hidden_dims=(4,)),
            layers=layers,
        )
    finally:
        torch.set_rng_state(rng_state)

    config = {
        "beta": 0.5,
        "credit_norm": "none",
        "target": None,
        "seed": seed,
    }

    return Case(
        state=state,
        prediction=prediction,
        multiplier=multiplier,
        config=config,
        free_activations=free_acts,
        nudged_activations=nudged_acts,
        weights=weights,
        geometry=geometry,
    )
