"""Reference implementation for PC-ALM Credit Assignment.

Delegates to computronium.ontology.credit.PCALMCredit (the source of truth).
This wrapper provides the uniform `step(case)` interface for parity/microbench.
"""

from typing import Any

import torch

from computronium.ontology.credit import (
    CreditAssignmentConfig,
    PCALMCredit,
    Phase,
)
from computronium.state import CompositeState


def _case_to_states(case: Any) -> dict:
    """Convert a test case to free/nudged states with dual variables."""
    # The nudged phase should have dual variables from PCALMDynamics settling
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

    # Add dual_vars to nudged state metrics (as PCALMDynamics does)
    if hasattr(case, "dual_vars") and case.dual_vars is not None:
        nudged_state.metrics = {"dual_vars_nudged": case.dual_vars}
    elif hasattr(case, "dual_vars_free") and case.dual_vars_free is not None:
        free_state.metrics = {"dual_vars": case.dual_vars_free}
        nudged_state.metrics = {"dual_vars_nudged": case.dual_vars_nudged}

    return {
        Phase.FREE: free_state,
        Phase.NUDGED: nudged_state,
    }


def step(case: Any) -> list[torch.Tensor]:
    """Execute reference credit assignment step.

    The case object contains activations, dual variables, and loss for
    computing pseudo-gradients. Returns list of pseudo-gradients per layer.
    """
    config = CreditAssignmentConfig.pc_alm(
        beta=case.config.get("beta_dual", 0.5),
        credit_norm=case.config.get("credit_norm", "rms"),
    )
    credit = PCALMCredit(config)

    # Get geometry from case
    geometry = case.geometry

    # Get states with dual variables
    states = _case_to_states(case)

    # Get loss - use the nudged output activations to compute a loss
    nudged_output = case.nudged_activations[-1]
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
