"""Deterministic test cases for the zeroth-order estimator.

These cases are intentionally small. They are used for parity tests,
smoke tests, and microbenchmarks. They are not scientific benchmarks.
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
    estimator_samples: int = 8,
    fd_step: float = 1e-2,
) -> Case:
    case = make_estimator_case(
        geometry_factory=lambda: FeedforwardGeometry(
            GeometryConfig.feedforward(input_dim=4, output_dim=4, hidden_dims=(4,))
        ).to(device),
        config={"estimator_samples": estimator_samples, "fd_step": fd_step},
        device=device,
        seed=seed,
    )
    return Case(
        state=case.state,
        activations=case.activations,
        nudged_activations=case.nudged_activations,
        config=case.config,
        geometry=case.geometry,
    )
