"""Accelerated kernel for Hybrid Credit Assignment (Triton rung).

Delegates to the reference implementation (Triton kernel TODO).
Provides the uniform `step(case)` interface.
"""

from typing import Any

from computronium.acceleration.backends import kernel_available

KERNEL_TECHNOLOGY = "triton"


def is_available() -> bool:
    """Check if the Triton kernel is available."""
    return kernel_available(KERNEL_TECHNOLOGY)


def step(case: Any) -> list:
    """Execute one accelerated step using the opaque case object."""
    from .reference import step as reference_step

    return reference_step(case)
