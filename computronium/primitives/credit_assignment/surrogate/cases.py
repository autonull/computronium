"""Deterministic test cases for the straight-through surrogate credit.

These cases are intentionally small. They are used for parity tests,
smoke tests, and microbenchmarks. They are not scientific benchmarks.
"""

from dataclasses import dataclass
from typing import Any

import torch

from computronium.harness import seeded_rng
from computronium.ontology.geometry import Geometry, GeometryConfig, RoutingGeometry


@dataclass(frozen=True, slots=True)
class Case:
    state: torch.Tensor
    activations: list[torch.Tensor]
    nudged_activations: list[torch.Tensor]
    config: dict[str, Any]
    geometry: Geometry


def make_case(
    *,
    device: str = "cpu",
    dtype: torch.dtype = torch.float32,
    seed: int = 0,
) -> Case:
    generator = torch.Generator(device=device).manual_seed(seed)
    state = torch.randn(2, 4, device=device, dtype=dtype, generator=generator)

    with seeded_rng(seed):
        geometry = RoutingGeometry(
            GeometryConfig.routing(
                input_dim=4,
                output_dim=4,
                hidden_dims=(4,),
                num_experts=4,
                top_k=1,
                routing_temperature=0.1,
            )
        )

    activations = geometry.forward_with_intermediates(state)
    target = torch.randint(0, 4, (2,), generator=generator)
    config: dict[str, Any] = {"seed": seed, "target": target}
    return Case(
        state=state,
        activations=activations,
        nudged_activations=activations,
        config=config,
        geometry=geometry,
    )
