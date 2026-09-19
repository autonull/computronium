"""Accelerated kernel for PC-ALM Credit Assignment.

Delegates to reference implementation (Triton kernel TODO).
Provides uniform `step(case)` interface.
"""

from typing import Any

from computronium.acceleration.backends import kernel_available

KERNEL_TECHNOLOGY = "triton"


def is_available() -> bool:
    """Check if Triton kernel is available."""
    return kernel_available(KERNEL_TECHNOLOGY)


def step(case: Any) -> list:
    """
    Execute one accelerated step using the opaque case object.

    Currently falls back to reference since Triton kernel is not implemented.
    """
    if not is_available():
        from .reference import step as reference_step

        return reference_step(case)

    # TODO: Implement Triton PC-ALM credit kernel
    # For now, fall back to reference
    from .reference import step as reference_step

    return reference_step(case)
