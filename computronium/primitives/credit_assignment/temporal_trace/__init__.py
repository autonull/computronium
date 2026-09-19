"""
Temporal Trace Credit (STDP) primitive.

This primitive implements spike-timing correlations for credit assignment.

Reference implementation:
    computronium.primitives.credit_assignment.temporal_trace.reference

Accelerated kernel:
    computronium.primitives.credit_assignment.temporal_trace.kernel
"""

from computronium.acceleration.registry import register

from .cases import make_case
from .kernel import step as kernel_step
from .reference import step as reference_step
from .spec import SPEC

register(SPEC)  # ruff: ignore[non-empty-init-module] (registration side effect required)

__all__ = [
    "SPEC",
    "kernel_step",
    "make_case",
    "reference_step",
]
