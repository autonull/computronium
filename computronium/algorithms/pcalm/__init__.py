# ruff: noqa: PLC0415
"""PC-ALM algorithm.

Composes primitives into a named method. Wraps
computronium.core.system_trainer.compose_joint_system for PC-ALM.

Reference implementation:
    computronium.algorithms.pcalm.reference

Accelerated kernel:
    computronium.algorithms.pcalm.kernel
"""

# Register the spec when this module is imported
from computronium.acceleration.registry import register as _register

from .cases import make_case
from .factory import create_pc_alm_mlp
from .kernel import step as kernel_step
from .reference import step as reference_step
from .spec import SPEC

_register(SPEC)

__all__ = [
    "SPEC",
    "create_pc_alm_mlp",
    "kernel_step",
    "make_case",
    "reference_step",
]
