"""Accelerated kernel for Fast-Weight algorithm.

Delegates to fast_weight primitive kernel where possible.
"""

from typing import Any

KERNEL_TECHNOLOGY = "triton"


def is_available() -> bool:
    """No fused fast-weight kernel exists; the reference path is the only rung."""
    return False


def step(case: Any) -> Any:
    """Execute one accelerated training step using the opaque case object."""
    if not is_available():
        from .reference import step as reference_step

        return reference_step(case)

    # For now, delegate to reference implementation
    from .reference import step as reference_step

    return reference_step(case)
