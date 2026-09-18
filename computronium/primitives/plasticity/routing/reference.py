"""Reference implementation for Routing Plasticity.

Delegates to computronium.core.plasticity.routing.RoutingPlasticity (the source of truth).
This wrapper provides the uniform `step(case)` interface for parity/microbench.
"""

from typing import Any

import torch

from computronium.core.plasticity.routing import RoutingPlasticity
from computronium.state import CompositeState


class _MockContext:
    """Minimal mock context for testing - only needs theta for training detection."""

    def __init__(self, device: torch.device):
        self.theta: dict[str, torch.Tensor] = {}
        self._device = device

    @property
    def device(self) -> torch.device:
        return self._device


def _case_to_psi(case: Any) -> dict[str, torch.Tensor]:
    """Extract plastic state from case."""
    return {
        "gate_logits": case.gate_logits,
        "active_routes": case.active_routes,
    }


def _case_to_composite_state(case: Any) -> CompositeState:
    """Convert a test case to a CompositeState for RoutingPlasticity."""
    state = CompositeState(
        activity={
            "x": case.pre_activity,
        },
        plastic={},
        substrate={},
    )
    return state


def _case_to_context(case: Any) -> _MockContext:
    """Create a minimal mock context from case."""
    return _MockContext(device=case.gate_logits.device)


def step(case: Any) -> dict[str, torch.Tensor]:
    """Execute reference plasticity step using the opaque case object.

    The case object is produced by cases.make_case and contains all
    tensors, parameters, and configuration needed for a small deterministic
    execution.

    Returns:
        Updated plastic state dict with gate_logits and active_routes.
    """
    plasticity = RoutingPlasticity(
        gate_dim=case.config["gate_dim"],
        temperature=case.config["temperature"],
        top_k=case.config.get("top_k"),
        decay=case.config["decay"],
        learning_rate=case.config["learning_rate"],
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
