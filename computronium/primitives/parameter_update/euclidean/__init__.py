# ruff: file-ignore[unsorted-imports]
# ruff: file-ignore[implicit-namespace-package]
# ruff: file-ignore[non-empty-init-module]
"""
Euclidean Update Primitive.

This primitive implements standard SGD with optional momentum (Euclidean update).

Reference implementation:
    computronium.primitives.parameter_update.euclidean.reference

Accelerated kernel:
    computronium.primitives.parameter_update.euclidean.kernel
"""

from computronium.acceleration.registry import register_module

globals().update(
    register_module(
        __name__,
        __doc__,
        has_factory=False,
    )
)
