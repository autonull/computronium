"""Reference implementation for Target Propagation algorithm.

Composes TP training step with transpose feedback and predictive settling.
"""

from typing import Any

from computronium.harness import (
    make_reference_system,
    reference_config,
    run_reference_step,
)
from computronium.ontology.credit import CreditAssignmentConfig, TargetInversionCredit
from computronium.ontology.dynamics import (
    PredictiveSettlingDynamics,
    StateDynamicsConfig,
)


def build_system(case: Any) -> Any:
    """Create the system the reference step runs on."""
    beta = case.config.get("beta", 0.1)
    dynamics = PredictiveSettlingDynamics(
        StateDynamicsConfig.predictive_settling(
            max_steps=case.config.get("settle_steps", 10),
            beta=beta,
        )
    )
    credit = TargetInversionCredit(
        CreditAssignmentConfig.target_inversion(
            beta=beta,
            feedback_scale=0.01,
        )
    )
    return make_reference_system(
        reference_config(case),
        credit,
        dynamics=dynamics,
    )


def step(case: Any) -> Any:
    """Execute one reference training step using the opaque case object."""
    return run_reference_step(case, build=build_system)
