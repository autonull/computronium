# ruff: file-ignore[unsorted-imports]
# ruff: file-ignore[implicit-namespace-package]
# ruff: file-ignore[non-empty-init-module]
"""
Role-Split Update Primitive.

This primitive implements per-name dispatcher: one rule on the named role, another everywhere else.

Reference implementation:
    computronium.primitives.parameter_update.role_split.reference

Accelerated kernel:
    computronium.primitives.parameter_update.role_split.kernel
"""

from computronium.acceleration.registry import register_module

globals().update(
    register_module(
        __name__,
        __doc__,
        has_factory=False,
    )
)
