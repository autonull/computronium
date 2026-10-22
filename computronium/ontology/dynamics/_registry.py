"""The dynamics backend registry, derived from the class declarations.

TODO34 §5.4: this used to be a hand-kept ``DYNAMICS_REGISTRY`` dict in
``__init__.py``, a second place to edit for every new primitive and a third
(after the class and the ``StateDynamicsConfig`` factory) that could silently
forget a key. The registry is now built as the classes are declared, so the
class carries its own ``dynamics_type`` alias — the same shape as
``@geometry_backend`` in ``ontology/geometry.py``, and the pattern the credit,
substrate and update layers should copy when they are migrated.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, TypeVar

from computronium.ontology._registry import ImplementationRegistry

if TYPE_CHECKING:
    from computronium.ontology.dynamics._dynamics import StateDynamics

T = TypeVar("T", bound="StateDynamics")

# Use string-based registry to avoid circular import
_DYNAMICS_REGISTRY = ImplementationRegistry("dynamics")
_DYNAMICS_REGISTRY.add_discovery_package("computronium.ontology.dynamics")


def dynamics_backend[T: StateDynamics](
    *dynamics_types: str,
) -> Callable[[type[T]], type[T]]:
    """Register a StateDynamics implementation under its ``dynamics_type`` keys.

    Args:
        dynamics_types: the keys a ``StateDynamicsConfig`` factory may name.
            Must match that factory's ``dynamics_type`` — the wiring lock
            proves the pairing in both directions.
    """
    return _DYNAMICS_REGISTRY.register(*dynamics_types)


# Backwards compatibility: the old dict interface
class _DynamicsRegistryView:
    """Read-only view of the registry for backwards compatibility."""

    def __getitem__(self, key: str) -> type[StateDynamics]:
        return _DYNAMICS_REGISTRY.get(key)

    def __contains__(self, key: str) -> bool:
        try:
            _DYNAMICS_REGISTRY.get(key)
            return True
        except KeyError:
            return False

    def __iter__(self):
        return iter(_DYNAMICS_REGISTRY.aliases())

    def get(self, key: str, default=None):
        try:
            return _DYNAMICS_REGISTRY.get(key)
        except KeyError:
            return default

    def keys(self):
        return _DYNAMICS_REGISTRY.aliases()

    def values(self):
        return [_DYNAMICS_REGISTRY.get(k) for k in self.keys()]

    def items(self):
        return [(k, _DYNAMICS_REGISTRY.get(k)) for k in self.keys()]


# Export the view for backwards compatibility with code using DYNAMICS_REGISTRY[key]
DYNAMICS_REGISTRY = _DynamicsRegistryView()  # type: ignore[assignment]

__all__ = ["DYNAMICS_REGISTRY", "dynamics_backend"]
