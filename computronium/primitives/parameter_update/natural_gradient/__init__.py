# ruff: file-ignore[unsorted-imports]
# ruff: file-ignore[implicit-namespace-package]
# ruff: file-ignore[non-empty-init-module]
"""
Natural Gradient Primitive.

This primitive implements the natural gradient parameter update with Fisher geometry preconditioning.

Reference implementation:
    computronium.primitives.parameter_update.natural_gradient.reference

Accelerated kernel:
    computronium.primitives.parameter_update.natural_gradient.kernel
"""

from computronium.acceleration.registry import register_module

globals().update(
    register_module(
        __name__,
        __doc__,
        has_factory=False,
    )
)
