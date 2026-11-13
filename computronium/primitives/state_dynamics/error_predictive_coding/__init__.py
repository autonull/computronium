# ruff: file-ignore[unsorted-imports]
# ruff: file-ignore[implicit-namespace-package]
# ruff: file-ignore[non-empty-init-module]
"""
Error Predictive Coding Primitive.

This primitive implements error-parameterized predictive coding: reverse-mode ad carries the loss gradient to every error.

Reference implementation:
    computronium.primitives.state_dynamics.error_predictive_coding.reference

Accelerated kernel:
    computronium.primitives.state_dynamics.error_predictive_coding.kernel
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
