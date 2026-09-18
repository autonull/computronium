"""Reference implementation for Forward-Forward algorithm.

Composes FF training step with layer-local goodness objectives.
"""

from dataclasses import dataclass
from typing import Any

import torch

from computronium.core.system_trainer import compose_system
from computronium.ontology.credit import CreditAssignmentConfig, LocalGoodnessCredit
from computronium.ontology.dynamics import InstantaneousDynamics, StateDynamicsConfig
from computronium.ontology.geometry import FeedforwardGeometry, GeometryConfig
from computronium.ontology.substrate import DigitalSubstrate, SubstrateConfig
from computronium.ontology.update import EuclideanUpdate, ParameterUpdateConfig


@dataclass(frozen=True, slots=True)
class _SystemConfig:
    input_dim: int = 4
    output_dim: int = 4
    hidden_dims: tuple[int, ...] = ()
    layer_lr: float = 0.03
    classifier_lr: float = 0.01
    threshold: float = 2.0
    device: str = "cpu"


def _make_ff_system(config: _SystemConfig) -> Any:
    """Create an FF system for testing."""
    substrate = DigitalSubstrate(SubstrateConfig.digital(device=config.device))
    geometry = FeedforwardGeometry(
        GeometryConfig.feedforward(
            input_dim=config.input_dim,
            output_dim=config.output_dim,
            hidden_dims=config.hidden_dims,
        )
    )
    dynamics = InstantaneousDynamics(StateDynamicsConfig.instantaneous())
    credit = LocalGoodnessCredit(CreditAssignmentConfig.local_goodness())
    update = EuclideanUpdate(ParameterUpdateConfig.euclidean(step_size=config.layer_lr))

    return compose_system(
        substrate=substrate,
        geometry=geometry,
        dynamics=dynamics,
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
            layer_lr=case.config.get("layer_lr", 0.03),
            classifier_lr=case.config.get("classifier_lr", 0.01),
            threshold=case.config.get("threshold", 2.0),
            device=case.state.device,
        )
        system = _make_ff_system(system_config)
        result = system.train_step(case.state, case.target)
    finally:
        torch.set_rng_state(rng_state)

    return result
