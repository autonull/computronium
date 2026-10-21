"""Reference implementation for Homeostatic.

Delegates to computronium.ontology.credit.HomeostaticCredit (the source of truth).
This wrapper provides the uniform `step(case)` interface for parity/microbench.
"""

from typing import Any

import torch

from computronium.harness import seeded_rng
from computronium.ontology.credit import CreditAssignmentConfig, HomeostaticCredit
from computronium.state import CompositeState


def _case_to_states(case: Any) -> dict:
    """Convert a test case to free/nudged states."""
    from computronium.ontology.credit import Phase

    free_state = CompositeState(
        activity={
            "x": case.state,
            "activations": case.activations,
        },
        plastic={},
        substrate={},
    )
    nudged_state = CompositeState(
        activity={
            "x": case.state,
            "activations": case.nudged_activations,
        },
        plastic={},
        substrate={},
    )
    return {
        Phase.FREE: free_state,
        Phase.NUDGED: nudged_state,
    }


def step(case: Any) -> list[torch.Tensor]:
    """Execute reference credit assignment step.

    The case object contains activations and loss for computing pseudo-gradients.
    Returns list of pseudo-gradients per layer.
    """
    config = CreditAssignmentConfig.homeostatic()
    credit = HomeostaticCredit(config)

    # Get geometry from case
    geometry = case.geometry

    # Get states
    states = _case_to_states(case)

    # Get loss - use the nudged output activations to compute a loss
    nudged_output = case.nudged_activations[-1]
    target = torch.zeros_like(nudged_output)
    loss = torch.nn.functional.mse_loss(nudged_output, target)

    # Compute pseudo-gradients with deterministic RNG
    with seeded_rng(case.config.get("seed", 0)):
        grads = credit.compute_pseudo_gradient(states, loss, geometry)

    return grads
