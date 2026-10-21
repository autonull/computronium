"""Accelerated kernel for Substrate-Coupled Plasticity.

Delegates to computronium.core.plasticity.substrate_coupled.SubstrateCoupledPlasticity.
Provides uniform `step(case)` interface.
"""

from typing import TYPE_CHECKING, Any

from computronium.acceleration.backends import kernel_available
from computronium.harness import seeded_rng

if TYPE_CHECKING:
    import torch

KERNEL_TECHNOLOGY = "triton"


def is_available() -> bool:
    return kernel_available(KERNEL_TECHNOLOGY)


def step(case: Any) -> Any:
    """Execute one accelerated step using the opaque case object."""
    if not is_available():
        from .reference import step as reference_step

        return reference_step(case)

    # Use accelerated implementation (falls back to reference for now)

    from computronium.core.plasticity.substrate_coupled import (
        SubstrateCoupledPlasticity,
    )
    from computronium.state import CompositeState

    class _MockContext:
        def __init__(self, device: torch.device):
            self._device = device

        @property
        def device(self) -> torch.device:
            return self._device

    plasticity = SubstrateCoupledPlasticity(**case.config)

    psi = {}
    z = CompositeState(
        activity={
            "x": case.pre_activity,
            "y": case.post_activity,
        },
        plastic={},
        substrate={},
    )
    context = _MockContext(device=case.pre_activity.device)  # type: ignore[arg-type]

    # Run with deterministic RNG state
    with seeded_rng(case.config.get("seed", 0)):
        new_psi = plasticity.step(psi, z, context)  # type: ignore[arg-type]

    return new_psi
