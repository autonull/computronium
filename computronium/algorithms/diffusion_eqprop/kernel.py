"""Accelerated kernel for DiffusionEqprop algorithm.

Uses torch_compile for acceleration where available.
"""

from typing import Any

from computronium.acceleration.backends import kernel_available

KERNEL_TECHNOLOGY = "torch_compile"


def is_available() -> bool:
    return kernel_available(KERNEL_TECHNOLOGY)


def step(case: Any) -> Any:
    """Execute one accelerated training step using the opaque case object."""
    if not is_available():
        from .reference import step as reference_step

        return reference_step(case)

    # TODO: Implement torch_compile accelerated path
    # For now, fall back to reference
    from .reference import step as reference_step

    return reference_step(case)
