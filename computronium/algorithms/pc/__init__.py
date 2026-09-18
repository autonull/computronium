# ruff: noqa: PLC0415
# ruff: noqa: INP001
"""Predictive Coding (PC) algorithm.

Hierarchical prediction error minimization. Wraps
computronium.core.presets.create_pc_mlp.

Reference implementation:
    computronium.algorithms.pc.reference

Accelerated kernel:
    computronium.algorithms.pc.kernel
"""

# Register the spec when this module is imported
from computronium.acceleration.registry import register as _register

from .cases import make_case
from .factory import create_pc_mlp
from .kernel import step as kernel_step
from .reference import step as reference_step
from .spec import SPEC

_register(SPEC)  # noqa: RUF067

__all__ = [
    "SPEC",
    "create_pc_mlp",
    "kernel_step",
    "make_case",
    "reference_step",
]
