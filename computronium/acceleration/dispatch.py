"""Backend Dispatch Policy.

One dispatch answers "which rung for this spec", and it can name the rung's
technology (TODO36 §4.3). The ladder has two rungs — ``reference`` and
``kernel`` — and the kernel rung is implemented in one technology, so a request
may name either.

    select_backend(spec, "auto")       -> the highest promoted rung
    select_backend(spec, "reference")  -> "reference"
    select_backend(spec, "kernel")     -> "kernel"
    select_backend(spec, "triton")     -> "kernel", or ValueError naming what exists

:func:`resolve_rung` is the same decision with the rest of the answer attached;
:func:`select_backend` is its ``rung`` field, so there is one implementation of
the policy rather than two that can disagree.

Both answer what the *spec* has. :func:`resolve_available_rung` answers what
this machine can run — the triton rung compiles per family, so the same request
is satisfiable for one family and not the next, which no field on the spec can
express. It returns the fallback alongside the rung rather than performing it
quietly, because a fallback nobody sees trains at a different speed and reports
the same number.
"""

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from computronium.acceleration.spec import (
        Backend,
        ImplementationSpec,
        KernelTechnology,
    )

__all__ = [
    "PROMOTED_STATUSES",
    "RungResolution",
    "SelectedRung",
    "resolve_available_rung",
    "resolve_rung",
    "select_backend",
]

#: Statuses at which a spec's kernel rung may be selected by ``"auto"``.
PROMOTED_STATUSES = frozenset({"kernel_verified", "microbenched", "campaign_ready"})

_TECHNOLOGIES: frozenset[str] = frozenset({
    "triton",
    "cuda",
    "torch_compile",
    "cupy",
    "numpy",
})


@dataclass(frozen=True, slots=True)
class SelectedRung:
    """A rung and everything the dispatch decided about it.

    Attributes:
        rung: which rung was selected.
        technology: what that rung is implemented in.
        entrypoint: the callable's dotted path, or ``None`` for the reference rung
            when the spec declares none.
        status: the spec's promotion status.
        promoted: whether ``"auto"`` would select this rung.
    """

    rung: Backend
    technology: KernelTechnology | None
    entrypoint: str | None
    status: str
    promoted: bool


def _reference(spec: ImplementationSpec) -> SelectedRung:
    return SelectedRung(
        rung="reference",
        technology="torch",
        entrypoint=spec.reference_entrypoint,
        status=spec.status,
        promoted=True,
    )


def _kernel(spec: ImplementationSpec) -> SelectedRung:
    return SelectedRung(
        rung="kernel",
        technology=spec.kernel_technology,
        entrypoint=spec.kernel_entrypoint,
        status=spec.status,
        promoted=spec.status in PROMOTED_STATUSES,
    )


def resolve_rung(spec: ImplementationSpec, requested: str = "auto") -> SelectedRung:
    """Resolve which rung of ``spec`` to run.

    Args:
        spec: the implementation to dispatch.
        requested: ``"auto"``, a rung name (``"reference"``, ``"kernel"``), or a
            technology (``"triton"``, ``"torch_compile"``, …). A technology
            request resolves to the kernel rung only when the spec's kernel rung
            is implemented in that technology.

    Returns:
        The selected rung, with its technology and entrypoint.

    Raises:
        ValueError: if the request names a rung the spec does not have, or a
            technology its kernel rung does not use. The message names what the
            spec does have, because "unavailable" without that is the defect
            TODO36 §4.2 removed.
    """
    if requested == "auto":
        if "kernel" in spec.supported_backends and spec.status in PROMOTED_STATUSES:
            return _kernel(spec)
        return _reference(spec)

    if requested == "reference":
        return _reference(spec)

    if requested == "kernel":
        if "kernel" not in spec.supported_backends:
            raise ValueError(_unavailable(spec, "kernel rung"))
        return _kernel(spec)

    if requested in _TECHNOLOGIES:
        if "kernel" not in spec.supported_backends:
            raise ValueError(_unavailable(spec, f"{requested} rung"))
        if spec.kernel_technology != requested:
            raise ValueError(_unavailable(spec, f"{requested} rung"))
        return _kernel(spec)

    raise ValueError(f"unknown backend request: {requested}")


def _unavailable(spec: ImplementationSpec, wanted: str) -> str:
    have = ", ".join(spec.supported_backends) or "nothing"
    technology = spec.kernel_technology or "unspecified"
    return (
        f"{spec.id} has no {wanted}: supported backends are {have}, "
        f"kernel technology is {technology}, status is {spec.status}"
    )


def select_backend(spec: ImplementationSpec, requested: str = "auto") -> str:
    """Select the rung name for an implementation.

    Args:
        spec: the implementation to dispatch.
        requested: ``"auto"``, ``"reference"``, ``"kernel"``, or a technology
            such as ``"triton"``.

    Returns:
        The selected rung: ``"reference"`` or ``"kernel"``.

    Raises:
        ValueError: if the request cannot be satisfied; see :func:`resolve_rung`.
    """
    return resolve_rung(spec, requested).rung


@dataclass(frozen=True, slots=True)
class RungResolution:
    """A rung decision together with whether the request was honoured.

    The fallback is a field rather than a branch at the call site because a
    silent fallback is the defect this tree keeps finding: a spec whose triton
    rung does not compile on this box dispatches to the reference rung, trains
    at a different speed, and reports the same number. Carrying the reason
    means the caller can log it, the status CLI can print it, and a test can
    assert on it — none of which a bare ``SelectedRung`` allows.

    Attributes:
        selected: the rung that will run.
        requested: what the caller asked for, verbatim.
        fell_back: whether ``selected`` is a lower rung than ``requested``.
        reason: why the fallback happened, or ``None`` when it did not.
    """

    selected: SelectedRung
    requested: str
    fell_back: bool = False
    reason: str | None = None


def resolve_available_rung(
    spec: ImplementationSpec, requested: str = "auto"
) -> RungResolution:
    """Resolve which rung will actually run here, falling back when it cannot.

    :func:`resolve_rung` answers what the spec *has*; this answers what this
    machine can *run*, which is a different question and was a second call at
    every dispatch site. The triton rung is the case that matters: it compiles
    per-family (TODO36 §4.2), so ``"triton"`` is satisfiable for one family on a
    box and unsatisfiable for the next, and the spec cannot say which.

    A request for a rung the spec does not have still raises — that is a
    programming error, not a property of the machine. Only the *runtime*
    availability of an existing rung falls back, and always says so.

    Args:
        spec: the implementation to dispatch.
        requested: as :func:`resolve_rung`.

    Returns:
        The rung that will run, and whether the request was honoured.

    Raises:
        ValueError: if ``spec`` has no such rung; see :func:`resolve_rung`.
    """
    selected = resolve_rung(spec, requested)
    if selected.technology != "triton" or selected.rung != "kernel":
        return RungResolution(selected=selected, requested=requested)
    if spec.family is None:
        return RungResolution(
            selected=_reference(spec),
            requested=requested,
            fell_back=True,
            reason=(
                f"{spec.id} declares a triton rung with no family, so there is "
                "nothing to compile-test it against; ran the reference rung"
            ),
        )
    from computronium.acceleration.availability import triton_rung_available

    if triton_rung_available(spec.family):
        return RungResolution(selected=selected, requested=requested)
    return RungResolution(
        selected=_reference(spec),
        requested=requested,
        fell_back=True,
        reason=(
            f"{spec.id}'s triton rung does not compile here for family "
            f"{spec.family}; ran the reference rung"
        ),
    )
