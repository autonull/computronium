"""Reference implementation for Rule State Plasticity.

Delegates to computronium.core.plasticity.rule_state.RuleStatePlasticity (the source of truth).
This wrapper provides the uniform `step(case)` interface for parity/microbench.
"""

from typing import TYPE_CHECKING, Any

from computronium.core.plasticity.rule_state import (
    RuleStatePlasticity,
)
from computronium.harness import seeded_rng
from computronium.state import CompositeState

if TYPE_CHECKING:
    import torch


def _case_to_composite_state(case: Any) -> CompositeState:
    """Convert a test case to a CompositeState for RuleStatePlasticity."""
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
        Updated plastic state dict.
    """
    # Set seed BEFORE creating plasticity to ensure deterministic initialization
    with seeded_rng(case.config.get("seed", 0)):
        plasticity = RuleStatePlasticity(
            num_operators=case.config.get("num_operators", 4),
            operator_dim=case.config.get("operator_dim", 8),
            controller_hidden=case.config.get("controller_hidden", 16),
            temperature=case.config.get("temperature", 1.0),
            learning_rate=case.config.get("learning_rate", 0.01),
            decay=case.config.get("decay", 0.99),
            device=case.state.device,
        )

        psi = case.psi
        z = _case_to_composite_state(case)
        context = _MockContext(device=case.state.device)

        new_psi = plasticity.step(psi, z, context)  # type: ignore[arg-type]

    return new_psi
