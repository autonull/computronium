# ruff: file-ignore[unsorted-imports]
# ruff: file-ignore[implicit-namespace-package]
# ruff: file-ignore[non-empty-init-module]
"""
Lion Update Primitive.

This primitive implements sign of the momentum interpolant with one o(1) buffer and no second moment.

Reference implementation:
    computronium.primitives.parameter_update.lion.reference

Accelerated kernel:
    computronium.primitives.parameter_update.lion.kernel
"""

from computronium.acceleration.registry import register_module

globals().update(
    register_module(
        __name__,
        __doc__,
        has_factory=False,
    )
)
