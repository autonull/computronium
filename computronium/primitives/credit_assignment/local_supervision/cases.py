"""Deterministic test cases for the local-supervision estimator.

These cases are intentionally small: parity, smoke, and microbenchmarks,
never scientific measurements.
"""

from dataclasses import dataclass
from typing import Any

from computronium.ontology.geometry import FeedforwardGeometry, Geometry, GeometryConfig
from computronium.primitives._common import make_estimator_case


@dataclass(frozen=True, slots=True)
class Case:
    state: Any
    activations: list[Any]
    nudged_activations: list[Any]
    config: dict[str, Any]
    geometry: Geometry


def make_case(
    *,
    device: str = "cpu",
    seed: int = 0,
) -> Case:
    case = make_estimator_case(
        geometry_factory=lambda: FeedforwardGeometry(
            GeometryConfig.feedforward(input_dim=8, output_dim=4, hidden_dims=(8, 8))
        ).to(device),
        config={},
        device=device,
        seed=seed,
        width=8,
        num_classes=4,
    )
    return Case(
        state=case.state,
        activations=case.activations,
        nudged_activations=case.nudged_activations,
        config=case.config,
        geometry=case.geometry,
    )
