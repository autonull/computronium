"""Reference implementation for PC-ALM algorithm.

Composes PC-ALM primitives into a full training step.
"""

from typing import Any

from computronium.harness import (
    make_joint_reference_system,
    reference_config,
    run_reference_step,
)
from computronium.ontology.credit import CreditAssignmentConfig, PCALMCredit
from computronium.ontology.dynamics import PCALMDynamics, StateDynamicsConfig
from computronium.ontology.geometry import FeedforwardGeometry, GeometryConfig
from computronium.ontology.plasticity import NullPlasticity


def build_system(case: Any) -> Any:
    """Create the system the reference step runs on."""
    config = reference_config(case)
    dynamics = PCALMDynamics(
        StateDynamicsConfig.pc_alm(
            max_steps=case.config.get("steps", 3),
            step_size=case.config.get("step_size", 0.1),
            rho=case.config.get("rho", 1.0),
            beta=case.config.get("beta", 0.5),
            prospective_leak=case.config.get("prospective_leak", 0.0),
            convergence_threshold=case.config.get("tol", 1e-4),
        )
    )
    geometry = FeedforwardGeometry(
        GeometryConfig.feedforward(
            input_dim=config.input_dim,
            output_dim=config.output_dim,
            hidden_dims=config.hidden_dims,
        )
    ).to(config.device)
    return make_joint_reference_system(
        config,
        PCALMCredit(CreditAssignmentConfig.pc_alm()),
        NullPlasticity(),
        geometry=geometry,
        dynamics=dynamics,
    )


def step(case: Any) -> Any:
    """Execute one reference training step using the opaque case object.

    The case object is produced by cases.make_case and contains all
    tensors, parameters, and configuration needed for a small deterministic
    execution.
    """
    return run_reference_step(case, build=build_system)
