"""Reference implementation for Routing algorithm (6-D joint).

Composes Routing training step with RoutingPlasticity.
"""

from dataclasses import dataclass
from typing import Any

import torch

from computronium.core.system_trainer import compose_joint_system
from computronium.ontology.credit import BackpropCredit, CreditAssignmentConfig
from computronium.ontology.dynamics import InstantaneousDynamics, StateDynamicsConfig
from computronium.ontology.geometry import FeedforwardGeometry, GeometryConfig
from computronium.ontology.plasticity import RoutingPlasticity
from computronium.ontology.substrate import DigitalSubstrate, SubstrateConfig
from computronium.ontology.update import EuclideanUpdate, ParameterUpdateConfig


@dataclass(frozen=True, slots=True)
class _SystemConfig:
    input_dim: int = 4
    output_dim: int = 4
    hidden_dims: tuple[int, ...] = ()
    lr: float = 1e-3
    gate_dim: int = 8
    gate_init_scale: float = 0.1
    device: str = "cpu"


def _make_routing_system(config: _SystemConfig) -> Any:
    """Create a Routing system for testing."""
    substrate = DigitalSubstrate(SubstrateConfig.digital(device=config.device))
    geometry = FeedforwardGeometry(
        GeometryConfig.feedforward(
            input_dim=config.input_dim,
            output_dim=config.output_dim,
            hidden_dims=config.hidden_dims,
        )
    )
    dynamics = InstantaneousDynamics(StateDynamicsConfig.instantaneous())
    credit = BackpropCredit(CreditAssignmentConfig.gradient())
    update = EuclideanUpdate(ParameterUpdateConfig.euclidean(step_size=config.lr))
    plasticity = RoutingPlasticity(
        gate_dim=config.gate_dim,
        temperature=1.0,
        decay=0.99,
        learning_rate=0.01,
    )

    return compose_joint_system(
        substrate=substrate,
        geometry=geometry,
        dynamics=dynamics,
        plasticity=plasticity,
        credit=credit,
        update=update,
    )


def step(case: Any) -> Any:
    """Execute one reference training step using the opaque case object."""
    rng_state = torch.get_rng_state()
    torch.manual_seed(case.config.get("seed", 0))
    try:
        system_config = _SystemConfig(
            input_dim=case.state.shape[1],
            output_dim=case.config.get("output_dim", case.state.shape[1]),
            lr=case.config.get("lr", 1e-3),
            gate_dim=case.config.get("gate_dim", 8),
            gate_init_scale=case.config.get("gate_init_scale", 0.1),
            device=case.state.device,
        )
        system = _make_routing_system(system_config)
        result = system.train_step(case.state, case.target)
    finally:
        torch.set_rng_state(rng_state)

    return result
