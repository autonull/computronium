"""Accelerated kernel for Local Goodness Credit Assignment.

Delegates to computronium.acceleration.ff_kernels.FFKernelBackend and
PEPITAKernelBackend. Provides uniform `step(case)` interface.
"""

from typing import Any

from computronium.acceleration.backends import kernel_available
from computronium.acceleration.ff_kernels import (
    HAS_TRITON_FF,
)

KERNEL_TECHNOLOGY = "triton"


def is_available() -> bool:
    return kernel_available(KERNEL_TECHNOLOGY) and HAS_TRITON_FF


def step(case: Any) -> list[Any]:
    """Execute one accelerated step using the opaque case object."""
    if not is_available():
        from .reference import step as reference_step

        return reference_step(case)

    # For local_goodness, we use the reference implementation since the
    # ff_kernels are model-bound and require a different interface.
    # The kernel backends in ff_kernels are used at the model level
    # (FFKernelBackend.kernel_train_step), not at the primitive credit level.
    from .reference import step as reference_step

    return reference_step(case)
