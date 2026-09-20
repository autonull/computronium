# ruff: file-ignore[unsorted-imports]
# ruff: file-ignore[implicit-namespace-package]
"""MomentumEqprop algorithm.

Momentum Equilibrium Propagation with heavy-ball dynamics

Reference implementation:
    computronium.algorithms.momentum_eqprop.reference

Accelerated kernel:
    computronium.algorithms.momentum_eqprop.kernel
"""

# Register the spec when this module is imported
from computronium.acceleration.registry import register as _register

from .cases import make_case
from .factory import create_momentum_eqprop_mlp
from .kernel import step as kernel_step
from .reference import step as reference_step
from .spec import SPEC

_register(SPEC)  # noqa: RUF067

__all__ = [
    "SPEC",
    "create_momentum_eqprop_mlp",
    "kernel_step",
    "make_case",
    "reference_step",
]
