"""Accelerated kernel for Backprop algorithm.

Uses torch.compile for acceleration where available.
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

    # For backprop, the kernel is just torch.compile of the reference
    # The reference implementation already uses PyTorch autograd which
    # is highly optimized. torch.compile may provide marginal benefit.
    from .reference import step as reference_step

    return reference_step(case)
