"""Accelerated kernel for Target Inversion.

Delegates to computronium.ontology.credit.TargetInversionCredit with triton acceleration.
Provides uniform `step(case)` interface.
"""

from typing import Any

from computronium.acceleration.backends import kernel_available

KERNEL_TECHNOLOGY = "triton"


def is_available() -> bool:
    return kernel_available(KERNEL_TECHNOLOGY)


def step(case: Any) -> Any:
    """Execute one accelerated step using the opaque case object."""
    if not is_available():
        from .reference import step as reference_step

        return reference_step(case)

    # Use accelerated implementation
    import torch

    from computronium.ontology.credit import (
        CreditAssignmentConfig,
        Phase,
        TargetInversionCredit,
    )
    from computronium.state import CompositeState

    config = CreditAssignmentConfig.target_inversion(
        beta=case.config.get("beta", 0.5),
    )

    # Get geometry from case
    geometry = case.geometry

    # Get states
    target = case.config.get("target", 0)
    if not isinstance(target, torch.Tensor):
        target = torch.tensor(
            [target] * case.state.shape[0], device=case.state.device, dtype=torch.long
        )
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
            "y": target,
        },
        plastic={},
        substrate={},
    )
    states = {Phase.FREE: free_state, Phase.NUDGED: nudged_state}

    # Get loss
    nudged_output = case.nudged_activations[-1]
    target_tensor = torch.zeros_like(nudged_output)
    loss = torch.nn.functional.mse_loss(nudged_output, target_tensor)

    # Compute pseudo-gradients with deterministic RNG
    rng_state = torch.get_rng_state()
    torch.manual_seed(case.config.get("seed", 0))
    try:
        credit = TargetInversionCredit(config)
        grads = credit.compute_pseudo_gradient(states, loss, geometry)
    finally:
        torch.set_rng_state(rng_state)

    return grads
