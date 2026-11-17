"""Accelerated kernel for the exact RTRL reference.

The Triton path is not implemented yet; this delegates to the reference so
the uniform ``step(case)`` interface stays available on every backend.
"""

from typing import Any

from computronium.acceleration.backends import kernel_available

KERNEL_TECHNOLOGY = "triton"


def is_available() -> bool:
    return kernel_available(KERNEL_TECHNOLOGY)


def step(case: Any) -> Any:
    from .reference import step as reference_step

    return reference_step(case)
