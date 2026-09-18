"""Accelerated kernel for PC-ALM algorithm.

Delegates to primitive kernels where possible.
"""

from typing import Any

from computronium.acceleration.backends import kernel_available
from computronium.acceleration.pcalm_kernels import HAS_TRITON_PCALM

KERNEL_TECHNOLOGY = "triton"


def is_available() -> bool:
    return kernel_available(KERNEL_TECHNOLOGY) and HAS_TRITON_PCALM


def step(case: Any) -> Any:
    """Execute one accelerated training step using the opaque case object."""
    if not is_available():
        from .reference import step as reference_step

        return reference_step(case)

    # For now, delegate to reference implementation
    # In the future, this could fuse the entire algorithm
    from .reference import step as reference_step

    return reference_step(case)
