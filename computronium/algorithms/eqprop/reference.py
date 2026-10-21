"""Reference implementation for Equilibrium Propagation algorithm.

Composes EqProp training step using energy minimization dynamics.
"""

from typing import Any

from computronium.harness import (
    make_reference_system,
    reference_config,
    run_reference_step,
)
from computronium.ontology.credit import CreditAssignmentConfig, ThermodynamicContrast
from computronium.ontology.dynamics import (
    EnergyMinimizationDynamics,
    StateDynamicsConfig,
)
from computronium.ontology.geometry import GeometryConfig, RecurrentGeometry


def build_system(case: Any) -> Any:
    """Create the system the reference step runs on."""
    config = reference_config(case, hidden_dims=case.config.get("hidden_dims", (8,)))
    beta = case.config.get("beta", 0.5)
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
            max_steps=case.config.get("steps", 20),
            step_size=case.config.get("step_size", 0.1),
            beta=beta,
        )
    )
    credit = ThermodynamicContrast(
        CreditAssignmentConfig.thermodynamic_contrast(beta=beta)
    )
    return make_reference_system(
        config,
        credit,
        geometry=geometry,
        dynamics=dynamics,
    )


def step(case: Any) -> Any:
    """Execute one reference training step using the opaque case object."""
    return run_reference_step(case, build=build_system)
