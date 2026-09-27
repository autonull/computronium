"""Reference implementation for Reverse Mode.

Delegates to computronium.ontology.credit.GradientCredit (the source of truth).
This wrapper provides the uniform `step(case)` interface for parity/microbench.
"""

from typing import Any

import torch

from computronium.ontology.credit import CreditAssignmentConfig, GradientCredit
from computronium.state import CompositeState


def _recompute_activations(geometry, input_tensor: torch.Tensor) -> list[torch.Tensor]:
    """Recompute activations by running forward pass through geometry."""
    activations = [input_tensor]
    x = input_tensor
    for layer in geometry._layers:
        x = layer(x)
        activations.append(x)
    return activations


def _case_to_states(case: Any) -> dict:
    """Convert a test case to free/nudged states."""
    # Recompute activations fresh for each call to maintain autograd graph
    free_activations = _recompute_activations(case.geometry, case.state)
    nudged_activations = _recompute_activations(
        case.geometry, case.nudged_activations[0]
    )

    free_state = CompositeState(
        activity={
            "x": free_activations[0],
            "activations": free_activations,
        },
        plastic={},
        substrate={},
    )
    nudged_state = CompositeState(
        activity={
            "x": nudged_activations[0],
            "activations": nudged_activations,
        },
        plastic={},
        substrate={},
    )
    return {
        "free": free_state,
        "nudged": nudged_state,
    }


def step(case: Any) -> list[torch.Tensor]:
    """Execute reference credit assignment step.

    The case object contains activations and loss for computing pseudo-gradients.
    Returns list of pseudo-gradients per layer.
    """
    config = CreditAssignmentConfig.gradient(
        beta=case.config.get("beta", 0.5),
    )
    credit = GradientCredit(config)

    # Get geometry from case
    geometry = case.geometry

    # Get states with fresh activations
    states = _case_to_states(case)

    # Get loss - use the nudged output activations to compute a loss
    # The loss must depend on the logits for autograd to work
    nudged_activations = _recompute_activations(
        case.geometry, case.nudged_activations[0]
    )
    nudged_output = nudged_activations[-1]
    target = torch.zeros_like(nudged_output)
    loss = torch.nn.functional.mse_loss(nudged_output, target)

    # Compute pseudo-gradients with deterministic RNG
    rng_state = torch.get_rng_state()
    torch.manual_seed(case.config.get("seed", 0))
    try:
        grads = credit.compute_pseudo_gradient(states, loss, geometry)
    finally:
        torch.set_rng_state(rng_state)

    return grads
