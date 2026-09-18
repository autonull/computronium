"""Reference implementation for Fast Weight Plasticity.

Delegates to computronium.core.plasticity.fast_weights.FastWeightPlasticity (the source of truth).
This wrapper provides the uniform `step(case)` interface for parity/microbench.
"""

from typing import Any

import torch

from computronium.core.plasticity.fast_weights import FastWeightPlasticity
from computronium.state import CompositeState


class _MockContext:
    """Minimal mock context for testing - only needs device property."""
    def __init__(self, device: torch.device):
        self._device = device

    @property
    def device(self) -> torch.device:
        return self._device


def _case_to_psi(case: Any) -> dict[str, torch.Tensor]:
    """Extract plastic state from case."""
    return {"fast_weights": case.fast_weights}


def _case_to_composite_state(case: Any) -> CompositeState:
    """Convert a test case to a CompositeState for FastWeightPlasticity."""
    state = CompositeState(
        activity={
            "x": case.pre_activity,
            "y": case.post_activity,
        },
        plastic={},
        substrate={},
    )
    return state


def _case_to_context(case: Any) -> _MockContext:
    """Create a minimal mock context from case."""
    return _MockContext(device=case.fast_weights.device)


def step(case: Any) -> dict[str, torch.Tensor]:
    """Execute reference plasticity step using the opaque case object.

    The case object is produced by cases.make_case and contains all
    tensors, parameters, and configuration needed for a small deterministic
    execution.

    Returns:
        Updated plastic state dict with fast_weights.
    """
    plasticity = FastWeightPlasticity(
        fast_weight_dim=case.config["fast_weight_dim"],
        decay=case.config["decay"],
        learning_rate=case.config["learning_rate"],
        outer_product_scale=case.config.get("outer_product_scale", 1.0),
    )

    psi = _case_to_psi(case)
    z = _case_to_composite_state(case)
    context = _case_to_context(case)

    # Run step with deterministic RNG state
    rng_state = torch.get_rng_state()
    torch.manual_seed(case.config.get("seed", 0))
    try:
        new_psi = plasticity.step(psi, z, context)  # type: ignore[arg-type]
    finally:
        torch.set_rng_state(rng_state)

    return new_psi
