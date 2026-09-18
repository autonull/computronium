# ruff: noqa: PLC0415
# ruff: noqa: INP001
"""Routing algorithm (6-D joint).

State-dependent gating with RoutingPlasticity. Wraps
computronium.core.presets.create_routing_mlp.

Reference implementation:
    computronium.algorithms.routing.reference

Accelerated kernel:
    computronium.algorithms.routing.kernel
"""

# Register the spec when this module is imported
from computronium.acceleration.registry import register as _register

from .cases import make_case
from .factory import create_routing_mlp
from .kernel import step as kernel_step
from .reference import step as reference_step
from .spec import SPEC

_register(SPEC)  # noqa: RUF067

__all__ = [
    "SPEC",
    "create_routing_mlp",
    "kernel_step",
    "make_case",
    "reference_step",
]
