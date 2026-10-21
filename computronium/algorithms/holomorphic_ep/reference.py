"""Reference implementation for HolomorphicEp algorithm.

Composes Holomorphic Ep training step using primitives.
"""

from typing import Any

from computronium.harness import (
    make_reference_system,
    reference_config,
    run_reference_step,
)
from computronium.ontology.credit import BackpropCredit, CreditAssignmentConfig


def _build_holomorphic_ep(case: Any) -> Any:
    """Create the system the reference step runs on."""
    return make_reference_system(
        reference_config(case),
        BackpropCredit(CreditAssignmentConfig.gradient()),
    )


def step(case: Any) -> Any:
    """Execute one reference training step using the opaque case object.

    The case object is produced by cases.make_case and contains all
    tensors, parameters, and configuration needed for a small deterministic
    execution.
    """
    return run_reference_step(case, build=_build_holomorphic_ep)
