# ruff: file-ignore[unsorted-imports]
# ruff: file-ignore[implicit-namespace-package]
# ruff: file-ignore[non-empty-init-module]
"""
Conflict-Adaptive Plasticity Primitive.

This primitive implements trace-decayed ridge readout whose decay is driven by detected readout/target conflict.

Reference implementation:
    computronium.primitives.plasticity.conflict_adaptive.reference

Accelerated kernel:
    computronium.primitives.plasticity.conflict_adaptive.kernel
"""

from computronium.acceleration.registry import register_module

globals().update(
    register_module(
        __name__,
        __doc__,
        has_factory=False,
        kernel_fn="step",
        reference_fn="step",
    )
)
