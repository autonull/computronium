"""Accelerated kernel for Homeostatic.

Delegates to computronium.ontology.credit.HomeostaticCredit with triton acceleration.
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

    from computronium.ontology.credit import CreditAssignmentConfig, HomeostaticCredit
    from computronium.state import CompositeState

    config = CreditAssignmentConfig.homeostatic()
    credit = HomeostaticCredit(config)

    # Get geometry from case
    geometry = case.geometry

    # Get states
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
    states = {Phase.FREE: free_state, Phase.NUDGED: nudged_state}

    # Get loss
    nudged_output = case.nudged_activations[-1]
    target = torch.zeros_like(nudged_output)
    loss = torch.nn.functional.mse_loss(nudged_output, target)

    # Run with deterministic RNG state
    rng_state = torch.get_rng_state()
    torch.manual_seed(case.config.get("seed", 0))
    try:
        grads = credit.compute_pseudo_gradient(states, loss, geometry)  # type: ignore[arg-type]
    finally:
        torch.set_rng_state(rng_state)
    return grads
