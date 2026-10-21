# ruff: file-ignore[unsorted-imports]
# ruff: file-ignore[implicit-namespace-package]
# ruff: file-ignore[non-empty-init-module]
"""
Temporal Trace Credit (STDP) primitive.

This primitive implements spike-timing correlations for credit assignment.

Reference implementation:
    computronium.primitives.credit_assignment.temporal_trace.reference

Accelerated kernel:
    computronium.primitives.credit_assignment.temporal_trace.kernel
"""

from computronium.acceleration.registry import register_module

globals().update(
    register_module(
        __name__,
        __doc__,
        has_factory=False,
    )
)
