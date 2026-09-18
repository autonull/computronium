"""Reference implementation for Spiking SNN algorithm.

Composes Spiking SNN training step with SpikeIntegrationDynamics and TemporalTraceCredit.
"""

from dataclasses import dataclass
from typing import Any

import torch

from computronium.core.system_trainer import compose_system
from computronium.ontology.credit import CreditAssignmentConfig, TemporalTraceCredit
from computronium.ontology.dynamics import SpikeIntegrationDynamics, StateDynamicsConfig
from computronium.ontology.geometry import FeedforwardGeometry, GeometryConfig
from computronium.ontology.substrate import DigitalSubstrate, SubstrateConfig
from computronium.ontology.update import EuclideanUpdate, ParameterUpdateConfig


@dataclass(frozen=True, slots=True)
class _SystemConfig:
    input_dim: int = 4
    output_dim: int = 4
    hidden_dims: tuple[int, ...] = ()
    lr: float = 1e-3
    max_steps: int = 30
    beta: float = 0.1
    threshold: float = 0.5
    device: str = "cpu"


def _make_spiking_snn_system(config: _SystemConfig) -> Any:
    """Create a Spiking SNN system for testing."""
    substrate = DigitalSubstrate(SubstrateConfig.digital(device=config.device))
    geometry = FeedforwardGeometry(
        GeometryConfig.feedforward(
            input_dim=config.input_dim,
            output_dim=config.output_dim,
            hidden_dims=config.hidden_dims,
        )
    )
    dynamics = SpikeIntegrationDynamics(
        StateDynamicsConfig.spike_integration(
            max_steps=config.max_steps,
            beta=config.beta,
            threshold=config.threshold,
        )
    )
    credit = TemporalTraceCredit(
        CreditAssignmentConfig.temporal_trace(
            tau_pre=0.9,
            tau_post=0.9,
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


def step(case: Any) -> Any:
    """Execute one reference training step using the opaque case object."""
    rng_state = torch.get_rng_state()
    torch.manual_seed(case.config.get("seed", 0))
    try:
        system_config = _SystemConfig(
            input_dim=case.state.shape[1],
            output_dim=case.config.get("output_dim", case.state.shape[1]),
            lr=case.config.get("lr", 1e-3),
            max_steps=case.config.get("max_steps", 30),
            beta=case.config.get("beta", 0.1),
            threshold=case.config.get("threshold", 0.5),
            device=case.state.device,
        )
        system = _make_spiking_snn_system(system_config)
        result = system.train_step(case.state, case.target)
    finally:
        torch.set_rng_state(rng_state)

    return result
