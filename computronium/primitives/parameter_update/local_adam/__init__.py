# ruff: file-ignore[unsorted-imports]
# ruff: file-ignore[implicit-namespace-package]
# ruff: file-ignore[non-empty-init-module]
"""
Local Adam Update Primitive.

This primitive implements per-tensor scalar second moment (lamb-style) over a first-moment direction.

Reference implementation:
    computronium.primitives.parameter_update.local_adam.reference

Accelerated kernel:
    computronium.primitives.parameter_update.local_adam.kernel
"""

from computronium.acceleration.registry import register_module

globals().update(
    register_module(
        __name__,
        __doc__,
        has_factory=False,
    )
)
