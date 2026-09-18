"""Accelerated kernel for Routing Plasticity.

Falls back to reference implementation. Provides uniform `step(case)` interface.
"""

from typing import Any

from computronium.acceleration.backends import kernel_available

KERNEL_TECHNOLOGY = "triton"


def is_available() -> bool:
    return kernel_available(KERNEL_TECHNOLOGY)


def step(case: Any) -> Any:
    """Execute one accelerated step using the opaque case object."""
    if not is_available():
        from .reference import step as reference_step

        return reference_step(case)

    # TODO: Implement routing plasticity kernel path
    # For now, delegate to reference
    from .reference import step as reference_step

    return reference_step(case)
