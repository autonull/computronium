"""Reference implementation for Fast-Weight algorithm (6-D joint).

Composes Fast-Weight training step with FastWeightPlasticity.
"""

from typing import Any

from computronium.harness import (
    make_joint_reference_system,
    reference_config,
    run_reference_step,
)
from computronium.ontology.credit import BackpropCredit, CreditAssignmentConfig
from computronium.ontology.plasticity import FastWeightPlasticity


def build_system(case: Any) -> Any:
    """Create the system the reference step runs on."""
    plasticity = FastWeightPlasticity(
        fast_weight_dim=case.config.get("fast_weight_dim", 32),
        decay=case.config.get("decay", 0.9),
        learning_rate=case.config.get("learning_rate", 0.1),
        outer_product_scale=1.0,
    )
    return make_joint_reference_system(
        reference_config(case),
        BackpropCredit(CreditAssignmentConfig.gradient()),
        plasticity,
    )


def step(case: Any) -> Any:
    """Execute one reference training step using the opaque case object."""
    return run_reference_step(case, build=build_system)
