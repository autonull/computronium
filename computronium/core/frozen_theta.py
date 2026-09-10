"""FrozenThetaAudit: hard θ-invariance audit (TODO18 1.3).

Stricter sibling of :func:`computronium.core.theta_audit.theta_audit`.
Snapshots every persistent tensor of a System — geometry parameters,
substrate state, optimizer moments — as clones, version counters, and
storage pointers, then verifies on exit that:

- values are bitwise identical (catches value mutations),
- ``Tensor._version`` counters are unchanged (catches in-place mutations
  even under a mutate-then-restore pattern),
- storage pointers are unchanged (catches alias rebinding).
"""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from typing import TYPE_CHECKING, Self

from torch import Tensor

if TYPE_CHECKING:
    from collections.abc import Iterator, Mapping

__all__ = [
    "FrozenThetaAudit",
    "FrozenThetaAuditReport",
    "FrozenThetaError",
    "frozen_theta_audit",
]


@dataclass(frozen=True, slots=True)
class FrozenThetaAuditReport:
    """Exact-diff verdict over all audited persistent state."""

    mutated: tuple[str, ...] = ()
    version_bumped: tuple[str, ...] = ()
    rebound: tuple[str, ...] = ()

    @property
    def invariant(self) -> bool:
        return not (self.mutated or self.version_bumped or self.rebound)

    def summary(self) -> str:
        return (
            f"mutated={list(self.mutated)} version_bumped={list(self.version_bumped)} "
            f"rebound={list(self.rebound)}"
        )


_AUDIT_NOT_EXITED = "assert_invariant called before the audited block exited"


class FrozenThetaError(AssertionError):
    """The frozen-θ contract was broken during an audited episode."""

    def __init__(self, report: FrozenThetaAuditReport) -> None:
        self.report = report
        super().__init__(f"frozen-θ contract violated: {report.summary()}")


@dataclass(slots=True)
class _Snapshot:
    clones: dict[str, Tensor]
    versions: dict[str, int]
    pointers: dict[str, int]


def _snapshot(tensors: Mapping[str, Tensor]) -> _Snapshot:
    return _Snapshot(
        clones={n: t.detach().clone() for n, t in tensors.items()},
        versions={n: t._version for n, t in tensors.items()},
        pointers={n: t.data_ptr() for n, t in tensors.items()},
    )


def _collect_persistent_state(system: object) -> dict[str, Tensor]:
    """Pull every persistent tensor a composed System owns."""
    tensors: dict[str, Tensor] = {}
    geometry = getattr(system, "geometry", None)
    if geometry is not None:
        tensors.update({
            f"geometry.{n}": t for n, t in getattr(geometry, "params", {}).items()
        })
    substrate = getattr(system, "substrate", None)
    if substrate is not None:
        state = getattr(substrate, "state", None)
        if isinstance(state, dict):
            tensors.update({
                f"substrate.{n}": t for n, t in state.items() if isinstance(t, Tensor)
            })
    optimizer = getattr(system, "optimizer", None)
    if optimizer is not None:
        for group_idx, group in enumerate(optimizer.param_groups):
            tensors.update({
                f"optimizer.g{group_idx}.{i}": p for i, p in enumerate(group["params"])
            })
    if not tensors:
        msg = "FrozenThetaAudit found no persistent tensors on the audited object"
        raise ValueError(msg)
    return tensors


class FrozenThetaAudit:
    """Context manager auditing a System's persistent state across a body.

    Usage::

        with FrozenThetaAudit(system, label="intra-episode") as audit:
            system.forward(x)
        audit.assert_invariant()
    """

    def __init__(self, system: object) -> None:
        self._system = system
        self._before: _Snapshot | None = None
        self.report: FrozenThetaAuditReport | None = None

    def __enter__(self) -> Self:
        self._before = _snapshot(_collect_persistent_state(self._system))
        return self

    def __exit__(self, *exc: object) -> None:
        if self._before is None:
            return
        before = self._before
        now = _collect_persistent_state(self._system)
        mutated: list[str] = []
        version_bumped: list[str] = []
        rebound: list[str] = []
        for name in before.clones.keys() | now.keys():
            t = now.get(name)
            snap = before.clones.get(name)
            if t is None or snap is None:
                rebound.append(name)
                continue
            if t.shape != snap.shape or not bool((t.detach() == snap).all()):
                mutated.append(name)
            if t._version != before.versions[name]:
                version_bumped.append(name)
            if t.data_ptr() != before.pointers[name]:
                rebound.append(name)
        self.report = FrozenThetaAuditReport(
            mutated=tuple(mutated),
            version_bumped=tuple(version_bumped),
            rebound=tuple(rebound),
        )

    def assert_invariant(self) -> None:
        """Raise unless no tensor was mutated, version-bumped, or rebound."""
        r = self.report
        if r is None:
            raise RuntimeError(_AUDIT_NOT_EXITED)
        if not r.invariant:
            raise FrozenThetaError(r)


@contextmanager
def frozen_theta_audit(
    system: object,
) -> Iterator[FrozenThetaAudit]:
    """Convenience wrapper: ``with frozen_theta_audit(system): ...``.

    Raises AssertionError at block exit if the frozen-θ contract broke.
    """
    audit = FrozenThetaAudit(system)
    with audit:
        yield audit
    audit.assert_invariant()
