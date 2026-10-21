"""Reference implementation for Target Propagation algorithm.

Composes TP training step using transpose feedback and predictive settling.
"""

from dataclasses import dataclass
from typing import Any

from computronium.core.system_trainer import compose_system
from computronium.harness import run_reference_step
from computronium.ontology.credit import CreditAssignmentConfig, TargetInversionCredit
from computronium.ontology.dynamics import (
    PredictiveSettlingDynamics,
    StateDynamicsConfig,
)
from computronium.ontology.geometry import FeedforwardGeometry, GeometryConfig
from computronium.ontology.substrate import DigitalSubstrate, SubstrateConfig
from computronium.ontology.update import EuclideanUpdate, ParameterUpdateConfig


@dataclass(frozen=True, slots=True)
class _SystemConfig:
    input_dim: int = 4
    output_dim: int = 4
    hidden_dims: tuple[int, ...] = ()
    lr: float = 1e-3
    beta: float = 0.1
    settle_steps: int = 10
    device: str = "cpu"


def _make_tp_system(config: _SystemConfig) -> Any:
    """Create a TP system for testing."""
    substrate = DigitalSubstrate(SubstrateConfig.digital(device=config.device))
    geometry = FeedforwardGeometry(
        GeometryConfig.feedforward(
            input_dim=config.input_dim,
            output_dim=config.output_dim,
            hidden_dims=config.hidden_dims,
        )
    )
    dynamics = PredictiveSettlingDynamics(
        StateDynamicsConfig.predictive_settling(
            max_steps=config.settle_steps,
            beta=config.beta,
        )
    )
    credit = TargetInversionCredit(
        CreditAssignmentConfig.target_inversion(
            beta=config.beta,
            feedback_scale=0.01,
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


def _build_tp(case: Any) -> Any:
    """Create the system the reference step runs on."""
    config = _SystemConfig(
        input_dim=case.state.shape[1],
        output_dim=case.config.get("output_dim", case.state.shape[1]),
        lr=case.config.get("lr", 1e-3),
        beta=case.config.get("beta", 0.1),
        settle_steps=case.config.get("settle_steps", 10),
        device=str(case.state.device),
    )
    return _make_tp_system(config)


def step(case: Any) -> Any:
    """Execute one reference training step using the opaque case object."""
    return run_reference_step(case, build=_build_tp)
