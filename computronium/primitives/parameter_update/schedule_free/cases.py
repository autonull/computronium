"""Deterministic test cases for the schedule-free AdamW rule.

These cases are intentionally small: parity, smoke, and microbenchmarks,
never scientific measurements.
"""

from dataclasses import dataclass
from typing import Any

from computronium.ontology.geometry import FeedforwardGeometry, Geometry, GeometryConfig
from computronium.primitives._common import make_activation_primitive_case


@dataclass(frozen=True, slots=True)
class Case:
    activations: list[Any]
    config: dict[str, Any]
    geometry: Geometry


def make_case(
    *,
    device: str = "cpu",
    seed: int = 0,
) -> Case:
    case = make_activation_primitive_case(
        geometry_factory=lambda: FeedforwardGeometry(
            GeometryConfig.feedforward(input_dim=4, output_dim=4, hidden_dims=(4,))
        ).to(device),
        config={},
        device=device,
        seed=seed,
    )
    return Case(
        activations=case.activations,
        config=case.config,
        geometry=case.geometry,
    )
