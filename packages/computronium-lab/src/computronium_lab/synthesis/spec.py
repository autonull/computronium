"""ProblemSpec DSL (TODO23 T23.1.1) — specify the problem, not the algorithm."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Literal

Objective = Literal["accuracy", "adaptation_speed", "stability", "latency", "memory"]
SubstrateName = Literal["digital", "memristive", "neuromorphic", "photonic", "quantum"]
KNOWN_OBJECTIVES: frozenset[str] = frozenset({
    "accuracy",
    "adaptation_speed",
    "stability",
    "latency",
    "memory",
})
KNOWN_SUBSTRATES: frozenset[str] = frozenset({
    "digital",
    "memristive",
    "neuromorphic",
    "photonic",
    "quantum",
})


@dataclass(frozen=True, slots=True)
class Constraints:
    """Hardware and runtime constraints on the synthesized mechanism."""

    compute_budget: str | None = None
    latency_ms: float | None = None
    memory_gb: float | None = None
    continual: bool = False
    local_credit: bool = False
    precision: str = "float32"
    substrate: str = "digital"

    def __post_init__(self) -> None:
        if self.substrate not in KNOWN_SUBSTRATES:
            raise ValueError(
                f"unknown substrate {self.substrate!r}; known: {sorted(KNOWN_SUBSTRATES)}"
            )


@dataclass(frozen=True, slots=True)
class ProblemSpec:
    """A problem specification: the input to the synthesis engine."""

    task: str
    dataset: str
    constraints: Constraints = field(default_factory=Constraints)
    objectives: tuple[str, ...] = ("accuracy",)
    exploration_budget: int = 3
    input_dim: int = 32
    num_classes: int = 4

    def __post_init__(self) -> None:
        if not self.task or not self.dataset:
            raise ValueError("task and dataset are required")
        unknown = set(self.objectives) - KNOWN_OBJECTIVES
        if unknown:
            raise ValueError(
                f"unknown objectives {sorted(unknown)}; known: {sorted(KNOWN_OBJECTIVES)}"
            )
        if self.exploration_budget < 1:
            raise ValueError("exploration_budget must be >= 1")

    def with_objectives(self, *objectives: str) -> ProblemSpec:
        return replace(self, objectives=objectives)

    def key(self) -> str:
        """Stable identity for budget accounting across identical specs."""
        c = self.constraints
        return (
            f"{self.task}/{self.dataset}/{c.substrate}/{c.precision}"
            f"/continual={c.continual}/local={c.local_credit}"
        )


__all__ = ["Constraints", "Objective", "ProblemSpec", "SubstrateName"]
