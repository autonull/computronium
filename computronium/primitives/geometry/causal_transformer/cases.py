"""Deterministic test cases for Causal Transformer Geometry.

These cases are intentionally small. They are used for parity tests,
smoke tests, and microbenchmarks. They are not scientific benchmarks.
"""

from dataclasses import dataclass
from typing import Any

import torch

from computronium.harness import seeded_rng
from computronium.ontology.geometry import GeometryConfig, TransformerGeometry


@dataclass(frozen=True, slots=True)
class Case:
    state: torch.Tensor
    config: dict[str, Any]
    geometry: TransformerGeometry


def make_case(
    *,
    device: str = "cpu",
    dtype: torch.dtype = torch.float32,
    seed: int = 0,
) -> Case:
    generator = torch.Generator(device=device).manual_seed(seed)

    state = torch.randint(0, 16, (2, 4), device=device, generator=generator)

    with seeded_rng(seed):
        geometry = TransformerGeometry(
            GeometryConfig.causal_transformer(
                vocab_size=16,
                d_model=8,
                n_layers=1,
                n_heads=2,
                seq_len=4,
            )
        )

    config = {"vocab_size": 16, "d_model": 8, "seq_len": 4, "seed": seed}

    return Case(state=state, config=config, geometry=geometry)
