"""Reference implementation for Local Goodness Credit Assignment.

Delegates to computronium.ontology.credit.LocalGoodnessCredit (the source of truth).
This wrapper provides the uniform `step(case)` interface for parity/microbench.
"""

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import torch

from computronium.ontology.credit import (
    CreditAssignmentConfig,
    LocalGoodnessCredit,
    Phase,
)
from computronium.ontology.system import SystemState


def _recompute_activations(geometry, input_tensor: torch.Tensor) -> list[torch.Tensor]:
    """Recompute activations by running forward pass through geometry."""
    activations = [input_tensor]
    x = input_tensor
    for layer in geometry._layers:
        x = layer(x)
        activations.append(x)
    return activations


def step(case: Any) -> list[torch.Tensor]:
    """Execute one reference step using the opaque case object.

    The case object is produced by cases.make_case and contains all
    tensors, parameters, and configuration needed for a small deterministic
    execution.

    Returns:
        List of pseudo-gradient tensors (one per weight matrix).
    """
    config = CreditAssignmentConfig.local_goodness(
        local_objective=case.config.get("local_objective", "ff"),
        feedback_scale=case.config.get("feedback_scale", 1.0),
        orthogonal_init=case.config.get("orthogonal_init", True),
        readout_error=case.config.get("readout_error", False),
        credit_norm=case.config.get("credit_norm", "rms"),
        learned_feedback=case.config.get("learned_feedback", False),
        feedback_lr=case.config.get("feedback_lr", 0.01),
        feedback_update_every=case.config.get("feedback_update_every", 10),
    )
    credit = LocalGoodnessCredit(config)

    # Recompute activations fresh for each call to maintain autograd graph
    free_activations = _recompute_activations(case.geometry, case.free_activations[0])
    nudged_activations = _recompute_activations(
        case.geometry, case.nudged_activations[0]
    )

    # Convert to SystemState objects for free and nudged phases
    free_state = SystemState(
        activations=free_activations,
        x=free_activations[0],
        y=case.config.get("target"),
    )
    nudged_state = SystemState(
        activations=nudged_activations,
        x=nudged_activations[0],
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
