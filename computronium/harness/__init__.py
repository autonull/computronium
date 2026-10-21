"""The harness primitive and algorithm reference steps share.

Every primitive and algorithm ships a ``cases`` module that builds a small
deterministic payload and a ``reference``/``kernel`` pair that consumes it. The
construction rules are the same everywhere — a seeded generator, a seeded
geometry, a config that names the seed — so they are written once here and each
harness contributes only what is specific to it.

The package loads lazily: a ``cases`` module needs only the case builders,
while a ``reference`` module also needs the system composition, and the two
have very different import costs.
"""

from __future__ import annotations

import importlib
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ._case import (
        AlgorithmCase,
        DynamicsCase,
        UpdateCase,
        case_generator,
        make_algorithm_case,
        make_dynamics_case,
        make_update_case,
        seeded_rng,
    )
    from ._geometry import geometry_forward
    from ._reference import (
        ReferenceSystemConfig,
        make_reference_system,
        reference_config,
        run_reference_step,
    )
    from ._update import update_geometry, update_pseudo_grads

#: Public symbol -> the submodule that defines it.
_symbol_to_module: dict[str, str] = {
    "AlgorithmCase": "_case",
    "DynamicsCase": "_case",
    "UpdateCase": "_case",
    "case_generator": "_case",
    "make_algorithm_case": "_case",
    "make_dynamics_case": "_case",
    "make_update_case": "_case",
    "seeded_rng": "_case",
    "geometry_forward": "_geometry",
    "ReferenceSystemConfig": "_reference",
    "make_reference_system": "_reference",
    "reference_config": "_reference",
    "run_reference_step": "_reference",
    "update_geometry": "_update",
    "update_pseudo_grads": "_update",
}

__all__ = [
    "AlgorithmCase",
    "DynamicsCase",
    "ReferenceSystemConfig",
    "UpdateCase",
    "case_generator",
    "geometry_forward",
    "make_algorithm_case",
    "make_dynamics_case",
    "make_reference_system",
    "make_update_case",
    "reference_config",
    "run_reference_step",
    "seeded_rng",
    "update_geometry",
    "update_pseudo_grads",
]


def __getattr__(name: str) -> Any:
    """Resolve a public symbol through the module that defines it."""
    module_name = _symbol_to_module.get(name)
    if module_name is None:
        raise AttributeError(f"module 'computronium.harness' has no attribute {name!r}")
    module = importlib.import_module(f"{__name__}.{module_name}")
    value = getattr(module, name)
    globals()[name] = value
    return value


def __dir__() -> list[str]:
    """List the public symbols."""
    return sorted(__all__)
