"""Reference implementation for PC-ALM algorithm.

Composes PC-ALM primitives into a full training step.
"""

from dataclasses import dataclass
from typing import Any

import torch

from computronium.core.system_trainer import compose_joint_system
from computronium.ontology.credit import CreditAssignmentConfig, PCALMCredit
from computronium.ontology.dynamics import PCALMDynamics, StateDynamicsConfig
from computronium.ontology.geometry import FeedforwardGeometry, GeometryConfig
from computronium.ontology.plasticity import NullPlasticity
from computronium.ontology.substrate import DigitalSubstrate, SubstrateConfig
from computronium.ontology.update import EuclideanUpdate, ParameterUpdateConfig


@dataclass(frozen=True, slots=True)
class _SystemConfig:
    input_dim: int = 4
    output_dim: int = 4
    hidden_dims: tuple[int, ...] = ()
    step_size: float = 0.1
    rho: float = 1.0
    beta: float = 0.5
    prospective_leak: float = 0.0
    max_steps: int = 3
    convergence_threshold: float = 1e-4
    lr: float = 1e-3
    device: str = "cpu"


def _make_pc_alm_system(config: _SystemConfig) -> Any:
    """Create a PC-ALM system for testing."""
    substrate = DigitalSubstrate(SubstrateConfig.digital(device=config.device))
    geometry = FeedforwardGeometry(
        GeometryConfig.feedforward(
            input_dim=config.input_dim,
            output_dim=config.output_dim,
            hidden_dims=config.hidden_dims,
        )
    )
    dynamics = PCALMDynamics(
        StateDynamicsConfig.pc_alm(
            max_steps=config.max_steps,
            step_size=config.step_size,
            rho=config.rho,
            beta=config.beta,
            prospective_leak=config.prospective_leak,
            convergence_threshold=config.convergence_threshold,
        )
    )
    plasticity = NullPlasticity()
    credit = PCALMCredit(CreditAssignmentConfig.pc_alm())
    update = EuclideanUpdate(ParameterUpdateConfig.euclidean(step_size=config.lr))

    return compose_joint_system(
        substrate=substrate,
        geometry=geometry,
        dynamics=dynamics,
        plasticity=plasticity,
        credit=credit,
        update=update,
    )


def step(case: Any) -> Any:
    """Execute one reference training step using the opaque case object.

    The case object is produced by cases.make_case and contains all
    tensors, parameters, and configuration needed for a small deterministic
    execution.
    """
    # Run training step with deterministic RNG state
    # Save RNG state BEFORE system creation (which may use RNG for init)
    rng_state = torch.get_rng_state()
    torch.manual_seed(case.config.get("seed", 0))
    try:
        # Create system
        system_config = _SystemConfig(
            input_dim=case.state.shape[1],
            output_dim=case.config.get("output_dim", case.state.shape[1]),
            step_size=case.config.get("step_size", 0.1),
            rho=case.config.get("rho", 1.0),
            beta=case.config.get("beta", 0.5),
            prospective_leak=case.config.get("prospective_leak", 0.0),
            max_steps=case.config.get("steps", 3),
            convergence_threshold=case.config.get("tol", 1e-4),
            lr=case.config.get("lr", 1e-3),
            device=case.state.device,
        )
        system = _make_pc_alm_system(system_config)

        # Run training step
        result = system.train_step(case.state, case.target)
    finally:
        torch.set_rng_state(rng_state)

    return result
