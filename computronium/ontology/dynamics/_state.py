"""The settle state contract — one surface, two algebras (TODO34 §5.3).

**The decision, written before the code** (the plan's sequencing rule):

    ``SystemState`` is *not* merged into ``CompositeState`` and neither
    replaces the other. They are two deliberate views of an intra-episode
    state and both are live: the 5-layer pipeline constructs ``SystemState``
    (``core/pipeline.py``) while every ``primitives/**/kernel.py`` reference
    and the joint/plasticity/continual paths construct ``CompositeState``
    (``z_t = (activity, plastic, substrate)``). What was wrong was not the
    existence of two views — it was that ``StateDynamics.settle`` *named one
    of them* while the runtime passed the other, so 11 dynamics classes
    carried an annotation that pyright correctly rejects and every
    implementation had to ``cast`` its own return value.

    The contract is therefore the **surface**, not the class:
    ``SettableState`` below is the minimum both algebras expose, and it is
    what ``settle``/``compute_energy`` are annotated with. Narrowing to a
    concrete algebra is explicit and structural (``is_system_state`` /
    ``is_composite_state``), so a caller that needs the z_t view asks for it
    instead of the settle code pretending it is there.

    Fields outside the surface (``energy``, ``dual_vars``, ``spike_counts``,
    ``spike_rasters``) exist only on ``SystemState``. They are read and
    written through the ``getattr``/``setattr`` accessors in
    ``_dynamics.py``, which is the honest encoding of "optional, and absent
    on the z_t view" — see ``_get_state_dual_vars``.

    *Rejected alternative*: making ``CompositeState`` canonical with an
    explicit flat adapter. It was measurably the larger diff — the compat
    properties on ``CompositeState`` (``x``/``activations``/``free_state``/
    ``nudged_state``) are read by the pipeline, the distributed trainer and
    the reference kernels, so the adapter would have had to be the default
    representation rather than an adapter.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, TypeIs, runtime_checkable

if TYPE_CHECKING:
    from torch import Tensor

    from computronium.ontology.system import SystemState
    from computronium.state import CompositeState


@runtime_checkable
class SettableState(Protocol):
    """The read surface ``StateDynamics.settle`` requires of a state.

    Satisfied structurally by both ``SystemState`` and ``CompositeState``.
    Implementations may rebuild the state rather than mutate it, so the
    protocol describes the *fields*, not the identity.

    Members are declared read-only so both algebras satisfy them
    covariantly: ``SystemState`` carries plain fields, ``CompositeState``
    carries properties over its ``activity`` mapping. The write side is
    therefore expressed through :func:`set_state_field` — every one of
    those properties has a setter, and a read-only Protocol cannot prove
    it.
    """

    @property
    def x(self) -> Tensor | None: ...

    @property
    def y(self) -> Tensor | None: ...

    @property
    def activations(self) -> list[Tensor] | Tensor | None: ...

    @property
    def free_state(self) -> list[Tensor] | Tensor | None: ...

    @property
    def nudged_state(self) -> list[Tensor] | Tensor | None: ...

    @property
    def loss(self) -> Tensor | float | None: ...

    @property
    def metrics(self) -> dict[str, float] | None: ...


def set_state_field(state: SettableState, name: str, value: object) -> None:
    """Write one settle output field on whichever algebra the state uses."""
    setattr(state, name, value)


def is_system_state(state: object) -> TypeIs[SystemState]:
    """Narrow to the flat 5-layer pipeline record."""
    from computronium.ontology.system import SystemState

    return isinstance(state, SystemState)


def is_composite_state(state: object) -> TypeIs[CompositeState]:
    """Narrow to the z_t = (activity, plastic, substrate) view.

    Structural rather than nominal: ``computronium.core.joint.state`` and
    ``computronium.state.composite`` are two import paths to the same
    record, and duck-typed callers must not have to know which they hold.
    """
    return isinstance(getattr(state, "activity", None), dict) and isinstance(
        getattr(state, "plastic", None), dict
    )


__all__ = [
    "SettableState",
    "is_composite_state",
    "is_system_state",
    "set_state_field",
]
