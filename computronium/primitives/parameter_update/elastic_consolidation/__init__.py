# ruff: file-ignore[import-outside-top-level]
# ruff: file-ignore[implicit-namespace-package]
"""Elastic Consolidation primitive.

This primitive implements the elastic weight consolidation (ewc) with fisher information

Reference implementation:
    computronium.primitives.parameter_update.elastic_consolidation.reference

Accelerated kernel:
    computronium.primitives.parameter_update.elastic_consolidation.kernel
"""

# Register the spec when this module is imported
from computronium.acceleration.registry import register as _register

from .cases import make_case
from .kernel import is_available
from .kernel import step as kernel_step
from .reference import step as reference_step
from .spec import SPEC

_register(SPEC)  # noqa: RUF067

__all__ = [
    "SPEC",
    "is_available",
    "kernel_step",
    "make_case",
    "reference_step",
]
