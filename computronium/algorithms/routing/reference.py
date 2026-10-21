"""Reference implementation for Routing algorithm (6-D joint).

Composes Routing training step with RoutingPlasticity.
"""

from typing import Any

from computronium.harness import (
    make_joint_reference_system,
    reference_config,
    run_reference_step,
)
from computronium.ontology.credit import BackpropCredit, CreditAssignmentConfig
from computronium.ontology.plasticity import RoutingPlasticity


def build_system(case: Any) -> Any:
    """Create the system the reference step runs on."""
    plasticity = RoutingPlasticity(
        gate_dim=case.config.get("gate_dim", 8),
        temperature=1.0,
        decay=0.99,
        learning_rate=0.01,
    )
    return make_joint_reference_system(
        reference_config(case),
        BackpropCredit(CreditAssignmentConfig.gradient()),
        plasticity,
    )


def step(case: Any) -> Any:
    """Execute one reference training step using the opaque case object."""
    return run_reference_step(case, build=build_system)
