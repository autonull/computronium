"""Deterministic test cases for Convolutional Geometry.

These cases are intentionally small. They are used for parity tests,
smoke tests, and microbenchmarks. They are not scientific benchmarks.
"""

from dataclasses import dataclass
from typing import Any

import torch

from computronium.harness import seeded_rng
from computronium.ontology.geometry import ConvGeometry, GeometryConfig


@dataclass(frozen=True, slots=True)
class Case:
    state: torch.Tensor
    config: dict[str, Any]
    geometry: ConvGeometry


def make_case(
    *,
    device: str = "cpu",
    dtype: torch.dtype = torch.float32,
    seed: int = 0,
) -> Case:
    generator = torch.Generator(device=device).manual_seed(seed)

    state = torch.randn(1, 1, 28, 28, device=device, dtype=dtype, generator=generator)

    with seeded_rng(seed):
        geometry = ConvGeometry(
            GeometryConfig.conv(
                input_dim=784,
                output_dim=10,
                conv_channels=(8, 16),
                kernel_size=3,
                in_channels=1,
                input_hw=(28, 28),
                pool_hw=(4, 4),
            )
        )

    config = {"input_hw": (28, 28), "in_channels": 1, "seed": seed}

    return Case(state=state, config=config, geometry=geometry)
