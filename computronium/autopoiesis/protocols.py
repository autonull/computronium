"""Autopoiesis-ready primitives (TODO23 T23.1.8).

Interfaces only — zero implementation. These Protocols define the operator
space TODO24's self-producing mechanism search will mutate over, without
constraining how mutation, fitness, or selection are realized.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from torch import Tensor


@runtime_checkable
class OperatorGenome(Protocol):
    """A mutable description of one ontology operator (e.g. a settle rule)."""

    def genome(self) -> dict[str, object]: ...

    def instantiate(self) -> object: ...


@runtime_checkable
class MutationOperator(Protocol):
    """Produces a perturbed genome from a parent genome."""

    def mutate(self, genome: dict[str, object], rng: object) -> dict[str, object]: ...


@runtime_checkable
class FitnessMetric(Protocol):
    """Scores an instantiated operator on a task batch."""

    def score(self, operator: object, batch: tuple[Tensor, Tensor]) -> float: ...


@runtime_checkable
class SelectionPolicy(Protocol):
    """Chooses survivors from a scored population."""

    def select(
        self, population: list[tuple[object, float]], k: int
    ) -> list[object]: ...


@runtime_checkable
class StagnationDetector(Protocol):
    """Decides whether the search has stalled and should be re-seeded."""

    def update(self, best_fitness: float) -> bool: ...


@runtime_checkable
class Constitution(Protocol):
    """Hard constraints every genome must satisfy before evaluation."""

    def admits(self, genome: dict[str, object]) -> bool: ...


__all__ = [
    "Constitution",
    "FitnessMetric",
    "MutationOperator",
    "OperatorGenome",
    "SelectionPolicy",
    "StagnationDetector",
]
