"""Reference implementation for Equilibrium Propagation algorithm.

Composes EqProp training step using energy minimization dynamics.
"""

from dataclasses import dataclass
from typing import Any

import torch

from computronium.core.system_trainer import compose_system
from computronium.ontology.credit import CreditAssignmentConfig, ThermodynamicContrast
from computronium.ontology.dynamics import (
    EnergyMinimizationDynamics,
    StateDynamicsConfig,
)
from computronium.ontology.geometry import GeometryConfig, RecurrentGeometry
from computronium.ontology.substrate import DigitalSubstrate, SubstrateConfig
from computronium.ontology.update import EuclideanUpdate, ParameterUpdateConfig


@dataclass(frozen=True, slots=True)
class _SystemConfig:
    input_dim: int = 4
    output_dim: int = 4
    hidden_dims: tuple[int, ...] = (8,)
    lr: float = 1e-3
    beta: float = 0.5
    max_steps: int = 20
    step_size: float = 0.1
    device: str = "cpu"


def _make_eqprop_system(config: _SystemConfig) -> Any:
    """Create an EqProp system for testing."""
    substrate = DigitalSubstrate(SubstrateConfig.digital(device=config.device))
    geometry = RecurrentGeometry(
        GeometryConfig.recurrent(
            input_dim=config.input_dim,
            output_dim=config.output_dim,
            hidden_dims=config.hidden_dims,
        ),
        hidden_dim=config.hidden_dims[-1] if config.hidden_dims else config.output_dim,
    )
    dynamics = EnergyMinimizationDynamics(
        StateDynamicsConfig.energy_minimization(
            max_steps=config.max_steps,
            step_size=config.step_size,
            beta=config.beta,
        )
    )
    credit = ThermodynamicContrast(
        CreditAssignmentConfig.thermodynamic_contrast(beta=config.beta)
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
            hidden_dims=case.config.get("hidden_dims", (8,)),
            lr=case.config.get("lr", 1e-3),
            beta=case.config.get("beta", 0.5),
            max_steps=case.config.get("steps", 20),
            step_size=case.config.get("step_size", 0.1),
            device=case.state.device,
        )
        system = _make_eqprop_system(system_config)
        result = system.train_step(case.state, case.target)
    finally:
        torch.set_rng_state(rng_state)

    return result
