"""Reference implementation for Forward-Forward algorithm.

Composes FF training step with layer-local goodness objectives.
"""

from typing import Any

from computronium.harness import (
    make_reference_system,
    reference_config,
    run_reference_step,
)
from computronium.ontology.credit import CreditAssignmentConfig, LocalGoodnessCredit


def build_system(case: Any) -> Any:
    """Create the system the reference step runs on."""
    return make_reference_system(
        reference_config(case, lr=case.config.get("layer_lr", 0.03)),
        LocalGoodnessCredit(CreditAssignmentConfig.local_goodness()),
    )


def step(case: Any) -> Any:
    """Execute one reference training step using the opaque case object."""
    return run_reference_step(case, build=build_system)
