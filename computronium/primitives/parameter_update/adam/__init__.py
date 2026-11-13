# ruff: file-ignore[unsorted-imports]
# ruff: file-ignore[implicit-namespace-package]
# ruff: file-ignore[non-empty-init-module]
"""
Adam Update Primitive.

This primitive implements per-coordinate first/second-moment adaptive update with bias correction.

Reference implementation:
    computronium.primitives.parameter_update.adam.reference

Accelerated kernel:
    computronium.primitives.parameter_update.adam.kernel
"""

from computronium.acceleration.registry import register_module

globals().update(
    register_module(
        __name__,
        __doc__,
        has_factory=False,
    )
)
