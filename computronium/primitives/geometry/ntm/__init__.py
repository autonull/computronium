# ruff: file-ignore[unsorted-imports]
# ruff: file-ignore[implicit-namespace-package]
"""NTM Geometry Primitive.

This primitive exposes NtmGeometry from the core ontology with the
standard primitive interface (spec, reference, kernel, cases).
"""

from computronium.acceleration.registry import register as _register
from computronium.acceleration.spec import ImplementationSpec as _ImplementationSpec

from .spec import SPEC
from .reference import forward as reference_forward
from .cases import Case, make_case

__all__ = [
    "SPEC",
    "Case",
    "_ImplementationSpec",
    "make_case",
    "reference_forward",
]

# Register this primitive's spec
_register(SPEC)  # ruff: ignore[non-empty-init-module]
