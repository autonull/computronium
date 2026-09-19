"""Reference implementation for Null Plasticity.

Delegates to computronium.ontology.plasticity.NullPlasticity (the source of truth).
This wrapper provides the uniform `step(case)` interface for parity/microbench.
"""

from typing import Any

import torch

from computronium.ontology.plasticity import NullPlasticity
from computronium.state import CompositeState


def _case_to_composite_state(case: Any) -> CompositeState:
    """Convert a test case to a CompositeState for NullPlasticity."""
    state = CompositeState(
        activity={"x": case.state},
        plastic={},
        substrate={},
    )
    return state


class _MockContext:
    """Minimal mock context for testing - only needs device property."""

    def __init__(self, device: torch.device):
        self._device = device

    @property
    def device(self) -> torch.device:
        return self._device


def step(case: Any) -> dict[str, torch.Tensor]:
    """Execute reference plasticity step using the opaque case object.

    The case object is produced by cases.make_case and contains all
    tensors, parameters, and configuration needed for a small deterministic
    execution.

    Returns:
        Unchanged plastic state dict.
    """
    plasticity = NullPlasticity()

    psi = case.psi
    z = _case_to_composite_state(case)
    context = _MockContext(device=case.state.device)

    # Run step with deterministic RNG state
    rng_state = torch.get_rng_state()
    torch.manual_seed(case.config.get("seed", 0))
    try:
        new_psi = plasticity.step(psi, z, context)  # type: ignore[arg-type]
    finally:
        torch.set_rng_state(rng_state)

    return new_psi
