"""Reference implementation for Predictive Coding algorithm.

Composes PC training step with predictive settling dynamics.
"""

from typing import Any

from computronium.harness import (
    make_reference_system,
    reference_config,
    run_reference_step,
)
from computronium.ontology.credit import CreditAssignmentConfig, LocalGoodnessCredit
from computronium.ontology.dynamics import (
    PredictiveSettlingDynamics,
    StateDynamicsConfig,
)
from computronium.ontology.geometry import GeometryConfig, RecurrentGeometry


def build_system(case: Any) -> Any:
    """Create the system the reference step runs on."""
    config = reference_config(case)
    geometry = RecurrentGeometry(
        GeometryConfig.recurrent(
            input_dim=config.input_dim,
            output_dim=config.output_dim,
            hidden_dims=config.hidden_dims,
        ),
        hidden_dim=config.hidden_dims[-1] if config.hidden_dims else config.output_dim,
    )
    dynamics = PredictiveSettlingDynamics(
        StateDynamicsConfig.predictive_settling(
            max_steps=case.config.get("steps", 30),
            beta=case.config.get("beta", 0.5),
        )
    )
    return make_reference_system(
        config,
        LocalGoodnessCredit(CreditAssignmentConfig.local_goodness()),
        geometry=geometry,
        dynamics=dynamics,
    )


def step(case: Any) -> Any:
    """Execute one reference training step using the opaque case object."""
    return run_reference_step(case, build=build_system)
