# ruff: file-ignore[import-outside-top-level]
# ruff: file-ignore[implicit-namespace-package]
"""Spike Integration primitive.

This primitive implements the spike integration dynamics (lif/izhikevich).

Reference implementation:
    computronium.primitives.state_dynamics.spike_integration.reference

Accelerated kernel:
    computronium.primitives.state_dynamics.spike_integration.kernel
"""

# Register the spec when this module is imported
from computronium.acceleration.registry import register as _register

from .cases import make_case
from .kernel import step as kernel_step
from .reference import step as reference_step
from .spec import SPEC

_register(SPEC)  # ruff: ignore[non-empty-init-module]

__all__ = [
    "SPEC",
    "kernel_step",
    "make_case",
    "reference_step",
]
