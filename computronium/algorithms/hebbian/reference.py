"""Reference implementation for Hebbian algorithm.

Composes Hebbian training step with local correlation updates.
"""

from typing import Any

from computronium.harness import (
    make_reference_system,
    reference_config,
    run_reference_step,
)
from computronium.ontology.credit import CreditAssignmentConfig, LocalGoodnessCredit


def _build_hebbian(case: Any) -> Any:
    """Create the system the reference step runs on."""
    return make_reference_system(
        reference_config(case),
        LocalGoodnessCredit(CreditAssignmentConfig.local_goodness()),
    )


def step(case: Any) -> Any:
    """Execute one reference training step using the opaque case object."""
    return run_reference_step(case, build=_build_hebbian)
