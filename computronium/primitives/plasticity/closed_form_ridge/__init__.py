# ruff: file-ignore[unsorted-imports]
# ruff: file-ignore[implicit-namespace-package]
"""Closed-form ridge plasticity primitive.

This primitive exposes ClosedFormRidgePlasticity from the core ontology
with the standard primitive interface (spec, reference, kernel, cases).
"""

from computronium.acceleration.registry import register as _register
from computronium.acceleration.spec import ImplementationSpec as _ImplementationSpec

from .cases import Case, make_case
from .reference import step as reference_step
from .spec import SPEC

__all__ = [
    "SPEC",
    "Case",
    "_ImplementationSpec",
    "make_case",
    "reference_step",
]

# Register this primitive's spec
_register(SPEC)  # ruff: ignore[non-empty-init-module]
