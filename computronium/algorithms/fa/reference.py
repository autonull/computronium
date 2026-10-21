"""Reference implementation for Feedback Alignment algorithm.

Composes FA training step using fixed random feedback matrices.
"""

from typing import Any

from computronium.harness import (
    make_reference_system,
    reference_config,
    run_reference_step,
)
from computronium.ontology.credit import CreditAssignmentConfig, RandomProjectionsCredit


def build_system(case: Any) -> Any:
    """Create the system the reference step runs on."""
    return make_reference_system(
        reference_config(case),
        RandomProjectionsCredit(
            CreditAssignmentConfig.random_projections(
                beta=0.5,
                feedback_scale=case.config.get("feedback_scale", 0.01),
            )
        ),
    )


def step(case: Any) -> Any:
    """Execute one reference training step using the opaque case object."""
    return run_reference_step(case, build=build_system)
