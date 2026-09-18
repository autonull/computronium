"""Accelerated kernel for Random Projections Credit.

Delegates to computronium.acceleration.fa_kernels or falls back to reference.
Provides uniform `step(case)` interface.
"""

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import torch

from computronium.acceleration.backends import kernel_available

KERNEL_TECHNOLOGY = "triton"


def is_available() -> bool:
    return kernel_available(KERNEL_TECHNOLOGY)


def step(case: Any) -> list[torch.Tensor]:
    """Execute one accelerated step using the opaque case object."""
    if not is_available():
        from .reference import step as reference_step

        return reference_step(case)

    # TODO: Implement FA kernel path for credit assignment
    # For now, delegate to reference
    from .reference import step as reference_step

    return reference_step(case)
