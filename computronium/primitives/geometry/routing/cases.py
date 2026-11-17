"""Deterministic test cases for the hard top-k routing geometry.

These cases are intentionally small. They are used for parity tests,
smoke tests, and microbenchmarks. They are not scientific benchmarks.
"""

from dataclasses import dataclass
from typing import Any

import torch

from computronium.harness import seeded_rng
from computronium.ontology.geometry import GeometryConfig, RoutingGeometry


@dataclass(frozen=True, slots=True)
class Case:
    state: torch.Tensor
    config: dict[str, Any]
    geometry: RoutingGeometry


def make_case(
    *,
    device: str = "cpu",
    dtype: torch.dtype = torch.float32,
    seed: int = 0,
) -> Case:
    generator = torch.Generator(device=device).manual_seed(seed)

    input_dim = 8
    state = torch.randn(2, input_dim, device=device, dtype=dtype, generator=generator)

    with seeded_rng(seed):
        geometry = RoutingGeometry(
            GeometryConfig.routing(
                input_dim=input_dim,
                output_dim=4,
                hidden_dims=(8,),
                num_experts=4,
                top_k=2,
                routing_temperature=1.0,
                init_scale=0.1,
            )
        )

    config = {
        "input_dim": input_dim,
        "output_dim": 4,
        "hidden_dims": (8,),
        "num_experts": 4,
        "top_k": 2,
        "routing_temperature": 1.0,
        "seed": seed,
    }

    return Case(state=state, config=config, geometry=geometry)
