"""Ontology utilities package.

Re-exports from the consolidated _utils module.
"""

from computronium.ontology._utils import (
    ConfigFactory,
    _learnable_weight_names,
    apply_norm,
    apply_pseudo_gradients,
)

__all__ = [
    "ConfigFactory",
    "_learnable_weight_names",
    "apply_norm",
    "apply_pseudo_gradients",
]
