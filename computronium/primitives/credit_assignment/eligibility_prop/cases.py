"""Deterministic test cases for the e-prop temporal estimator.

These cases are intentionally small: a three-step recurrent fixture with a
class target, for parity, smoke, and microbenchmarks only.
"""

from dataclasses import dataclass
from typing import Any

import torch

from computronium.ontology.geometry import Geometry, GeometryConfig, RecurrentGeometry


@dataclass(frozen=True, slots=True)
class Case:
    x: torch.Tensor
    y: torch.Tensor
    config: dict[str, Any]
    geometry: Geometry


def make_case(
    *,
    device: str = "cpu",
    seed: int = 0,
    time: int = 3,
    batch: int = 2,
    width: int = 4,
    classes: int = 3,
) -> Case:
    torch.manual_seed(seed)
    generator = torch.Generator(device=device).manual_seed(seed)
    x = torch.randn((time, batch, width), device=device, generator=generator)
    y = torch.randint(0, classes, (time, batch), device=device, generator=generator)
    geometry = RecurrentGeometry(
        GeometryConfig.feedforward(
            input_dim=width,
            output_dim=classes,
            hidden_dims=(width,),
            init_scale=0.2,
        )
    ).to(device)
    return Case(x=x, y=y, config={}, geometry=geometry)
