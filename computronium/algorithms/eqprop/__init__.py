# ruff: file-ignore[I001]
# ruff: file-ignore[INP001]
"""Equilibrium Propagation (EqProp) algorithm.

Energy-based learning with local contrastive updates. Wraps
computronium.core.presets.create_eqprop_mlp.

Reference implementation:
    computronium.algorithms.eqprop.reference

Accelerated kernel:
    computronium.algorithms.eqprop.kernel
"""

# Register the spec when this module is imported
from computronium.acceleration.registry import register as _register

from .cases import make_case
from .factory import create_eqprop_mlp
from .kernel import step as kernel_step
from .reference import step as reference_step
from .spec import SPEC

_register(SPEC)  # noqa: RUF067

__all__ = [
    "SPEC",
    "create_eqprop_mlp",
    "kernel_step",
    "make_case",
    "reference_step",
]
