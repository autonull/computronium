# ruff: file-ignore[unsorted-imports]
# ruff: file-ignore[implicit-namespace-package]
"""Energy Minimization primitive.

This primitive implements the energy-based settling (equilibrium propagation, hopfield, chl).

Reference implementation:
    computronium.primitives.state_dynamics.energy_minimization.reference

Accelerated kernel:
    computronium.primitives.state_dynamics.energy_minimization.kernel
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
