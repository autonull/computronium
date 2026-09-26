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

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable

    from computronium.ontology.dynamics._dynamics import StateDynamics

DYNAMICS_REGISTRY: dict[str, type[StateDynamics]] = {}


def dynamics_backend[T: StateDynamics](
    *dynamics_types: str,
) -> Callable[[type[T]], type[T]]:
    """Register a StateDynamics implementation under its ``dynamics_type`` keys.

    Args:
        dynamics_types: the keys a ``StateDynamicsConfig`` factory may name.
            Must match that factory's ``dynamics_type`` — the wiring lock
            proves the pairing in both directions.
    """

    def register(cls: type[T]) -> type[T]:
        for dynamics_type in dynamics_types:
            DYNAMICS_REGISTRY[dynamics_type] = cls  # type: ignore[assignment]
        return cls

    return register


__all__ = ["DYNAMICS_REGISTRY", "dynamics_backend"]
