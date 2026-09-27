"""Reference implementation for PEPITA Credit Assignment.

Delegates to computronium.ontology.credit.PepitaCredit (the source of truth).
This wrapper provides the uniform `step(case)` interface for parity/microbench.
"""

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import torch

from computronium.ontology.credit import (
    CreditAssignmentConfig,
    PepitaCredit,
    Phase,
)
from computronium.ontology.system import SystemState


def step(case: Any) -> list[torch.Tensor]:
    """Execute one reference step using the opaque case object.

    The case object is produced by cases.make_case and contains all
    tensors, parameters, and configuration needed for a small deterministic
    execution.

    Returns:
        List of pseudo-gradient tensors (one per weight matrix).
    """
    config = CreditAssignmentConfig.pepita(
        gamma=case.config.get("gamma", 0.05),
        feedback_matrix=case.config.get("feedback_matrix", None),
    )
    credit = PepitaCredit(config)

    # Convert to SystemState objects for free and nudged phases
    free_state = SystemState(
        activations=case.free_activations,
        x=case.free_activations[0],
        y=case.config.get("target"),
    )
    nudged_state = SystemState(
        activations=case.nudged_activations,
        x=case.nudged_activations[0],
        y=case.config.get("target"),
    )

    geometry = case.geometry

    states = {
        Phase.FREE: free_state,
        Phase.NUDGED: nudged_state,
    }

    # Compute pseudo-gradient
    grads = credit.compute_pseudo_gradient(states, None, geometry)
    return grads
