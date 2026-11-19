"""Primitives package — Single-source specification and execution interface.

This module provides the public API for the primitive layer (TODO97 migration).
Replaces ~380 per-primitive spec/cases/reference/kernel files with:
- protocol.py: StepResult, PrimitiveSpec, PrimitiveProtocol, ReferenceAdapter
- registry.py: 75 PrimitiveSpec rows in REGISTRY
"""

from computronium.primitives.protocol import (
    PrimitiveProtocol,
    PrimitiveSpec,
    ReferenceAdapter,
    StepResult,
)
from computronium.primitives.registry import (
    REGISTRY,
    count_primitives,
    get_primitive_spec,
    list_primitives,
)

__all__ = [
    "PrimitiveProtocol",
    "PrimitiveSpec",
    "REGISTRY",
    "ReferenceAdapter",
    "StepResult",
    "count_primitives",
    "get_primitive_spec",
    "list_primitives",
]
