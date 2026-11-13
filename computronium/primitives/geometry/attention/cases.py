"""Deterministic test cases for Attention Geometry.

These cases are intentionally small. They are used for parity tests,
smoke tests, and microbenchmarks. They are not scientific benchmarks.
"""

from dataclasses import dataclass
from typing import Any

import torch

from computronium.harness import seeded_rng
from computronium.ontology.geometry import AttentionGeometry, GeometryConfig


@dataclass(frozen=True, slots=True)
class Case:
    state: torch.Tensor
    config: dict[str, Any]
    geometry: AttentionGeometry


def make_case(
    *,
    device: str = "cpu",
    dtype: torch.dtype = torch.float32,
    seed: int = 0,
) -> Case:
    generator = torch.Generator(device=device).manual_seed(seed)

    state = torch.randn(2, 8, device=device, dtype=dtype, generator=generator)

    with seeded_rng(seed):
        geometry = AttentionGeometry(
            GeometryConfig.attention(
                input_dim=8,
                output_dim=4,
                hidden_dim=8,
                num_layers=2,
                num_heads=2,
            )
        )

    config = {"hidden_dim": 8, "num_heads": 2, "seed": seed}

    return Case(state=state, config=config, geometry=geometry)
