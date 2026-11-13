# ruff: file-ignore[unsorted-imports]
# ruff: file-ignore[implicit-namespace-package]
# ruff: file-ignore[non-empty-init-module]
"""
Analog Substrate Primitive.

This primitive implements analog device model with additive state noise and bounded weights.

Reference implementation:
    computronium.primitives.substrate.analog.reference

Accelerated kernel:
    computronium.primitives.substrate.analog.kernel
"""

from computronium.acceleration.registry import register_module

globals().update(
    register_module(
        __name__,
        __doc__,
        has_factory=False,
        kernel_fn="make_substrate",
        reference_fn="make_substrate",
    )
)
