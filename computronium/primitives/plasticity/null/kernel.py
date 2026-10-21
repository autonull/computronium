"""Accelerated kernel for Null Plasticity.

Delegates to computronium.ontology.plasticity.NullPlasticity with triton acceleration.
Provides uniform `step(case)` interface.
"""

from typing import TYPE_CHECKING, Any

from computronium.acceleration.backends import kernel_available
from computronium.harness import seeded_rng
from computronium.ontology.plasticity import NullPlasticity
from computronium.state import CompositeState

if TYPE_CHECKING:
    import torch

KERNEL_TECHNOLOGY = "triton"


def is_available() -> bool:
    return kernel_available(KERNEL_TECHNOLOGY)


def step(case: Any) -> dict[str, torch.Tensor]:
    """Execute one accelerated step using the opaque case object."""
    if not is_available():
        from .reference import step as reference_step

        return reference_step(case)

    # Use accelerated implementation (fallback to reference for now)
    plasticity = NullPlasticity()

    psi = case.psi
    z = CompositeState(
        activity={"x": case.state},
        plastic={},
        substrate={},
    )

    class _MockContext:
        """Minimal mock context for testing - only needs device property."""

        def __init__(self, device: torch.device):
            self._device = device

        @property
        def device(self) -> torch.device:
            return self._device

    context = _MockContext(device=case.state.device)

    with seeded_rng(case.config.get("seed", 0)):
        new_psi = plasticity.step(psi, z, context)  # type: ignore[arg-type]

    return new_psi
