# ruff: file-ignore[unsorted-imports]
# ruff: file-ignore[implicit-namespace-package]
# ruff: file-ignore[non-empty-init-module]
"""
Mean-Norm Update Primitive.

This primitive implements per-tensor mean-|g| magnitude normalization (the magnitude-only rung).

Reference implementation:
    computronium.primitives.parameter_update.mean_norm.reference

Accelerated kernel:
    computronium.primitives.parameter_update.mean_norm.kernel
"""

from computronium.acceleration.registry import register_module

globals().update(
    register_module(
        __name__,
        __doc__,
        has_factory=False,
    )
)
