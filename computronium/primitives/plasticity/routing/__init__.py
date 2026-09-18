# ruff: noqa: PLC0415
# ruff: noqa: INP001
"""Routing Plasticity primitive.

This primitive implements state-dependent pathway gating with Gumbel-Softmax
routing and per-unit modulation.

Reference implementation:
    computronium.primitives.plasticity.routing.reference

Accelerated kernel:
    computronium.primitives.plasticity.routing.kernel
"""

# Register the spec when this module is imported
from computronium.acceleration.registry import register as _register

from .cases import make_case
from .kernel import step as kernel_step
from .reference import step as reference_step
from .spec import SPEC

_register(SPEC)  # noqa: RUF067

__all__ = [
    "SPEC",
    "kernel_step",
    "make_case",
    "reference_step",
]
