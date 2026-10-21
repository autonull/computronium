"""Reference implementation for Feedback Alignment algorithm.

Composes FA training step using fixed random feedback matrices.
"""

from dataclasses import dataclass
from typing import Any

from computronium.core.system_trainer import compose_system
from computronium.harness import run_reference_step
from computronium.ontology.credit import CreditAssignmentConfig, RandomProjectionsCredit
from computronium.ontology.dynamics import InstantaneousDynamics, StateDynamicsConfig
from computronium.ontology.geometry import FeedforwardGeometry, GeometryConfig
from computronium.ontology.substrate import DigitalSubstrate, SubstrateConfig
from computronium.ontology.update import EuclideanUpdate, ParameterUpdateConfig


@dataclass(frozen=True, slots=True)
class _SystemConfig:
    input_dim: int = 4
    output_dim: int = 4
    hidden_dims: tuple[int, ...] = ()
    lr: float = 1e-3
    feedback_scale: float = 0.01
    device: str = "cpu"


def _make_fa_system(config: _SystemConfig) -> Any:
    """Create an FA system for testing."""
    substrate = DigitalSubstrate(SubstrateConfig.digital(device=config.device))
    geometry = FeedforwardGeometry(
        GeometryConfig.feedforward(
            input_dim=config.input_dim,
            output_dim=config.output_dim,
            hidden_dims=config.hidden_dims,
        )
    )
    dynamics = InstantaneousDynamics(StateDynamicsConfig.instantaneous())
    credit = RandomProjectionsCredit(
        CreditAssignmentConfig.random_projections(
            beta=0.5,
            feedback_scale=config.feedback_scale,
        )
    )
    update = EuclideanUpdate(ParameterUpdateConfig.euclidean(step_size=config.lr))

    return compose_system(
        substrate=substrate,
        geometry=geometry,
        dynamics=dynamics,
        credit=credit,
        update=update,
    )


def _build_fa(case: Any) -> Any:
    """Create the system the reference step runs on."""
    config = _SystemConfig(
        input_dim=case.state.shape[1],
        output_dim=case.config.get("output_dim", case.state.shape[1]),
        lr=case.config.get("lr", 1e-3),
        feedback_scale=case.config.get("feedback_scale", 0.01),
        device=str(case.state.device),
    )
    return _make_fa_system(config)


def step(case: Any) -> Any:
    """Execute one reference training step using the opaque case object."""
    return run_reference_step(case, build=_build_fa)
