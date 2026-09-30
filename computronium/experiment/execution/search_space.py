"""Canonical search space and proposal abstractions (WP14).

The abc3 architecture specifies:
    Policy.propose(SearchContext) -> Iterator[Proposal]

with the wrapper applying legality and novelty uniformly.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Protocol, Iterator, runtime_checkable

if TYPE_CHECKING:
    from computronium.experiment.schema.axis import AxisSpec
    from computronium.experiment.schema.coordinate import Coordinate, Schedule
    from computronium.experiment.schema.registries import ConstraintSpec, ObjectiveSpec
    from computronium.experiment.execution.budget import Budget, CostModel
    from computronium.experiment.evidence.store import RecordStore
    from computronium.experiment.schema.record import Record


@dataclass(frozen=True, slots=True)
class Domain:
    """Parameter domain specification."""

    lo: float | int
    hi: float | int
    scale: str = "LINEAR"  # LINEAR | LOG
    members: tuple[str, ...] = field(default_factory=tuple)  # For CATEGORICAL


@dataclass(frozen=True, slots=True)
class SearchSpace:
    """Canonical search space derived from RunSpec."""

    axes_snapshot: tuple["AxisSpec", ...]
    constraints: tuple["ConstraintSpec", ...]
    objectives: tuple["ObjectiveSpec", ...]
    tasks: tuple[str, ...]

    def active_axes_for(self, coord: "Coordinate") -> frozenset["AxisSpec"]:
        """Get active axes for a given coordinate."""
        active = []
        for axis in self.axes_snapshot:
            if axis.axis_kind.value == "structural":
                continue
            if axis.availability_predicate is None or axis.availability_predicate.evaluate(coord):
                active.append(axis)
        return frozenset(active)


@dataclass(frozen=True, slots=True)
class ProposalContext:
    """Context passed to every policy's propose()."""

    search_space: SearchSpace
    budget: "Budget"
    cost_model: "CostModel"
    evidence: "RecordStore"
    run_id: str


@dataclass(frozen=True, slots=True)
class Proposal:
    """Single proposal from a policy."""

    coordinate: "Coordinate"
    schedule: "Schedule"
    rationale: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def proposal_id(self) -> str:
        """Generate a unique ID for this proposal."""
        content = f"{self.coordinate.cell_key()}|{self.schedule.fidelity}|{self.schedule.seed}|{self.rationale}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]


class Policy(Protocol):
    """Protocol for proposal policies."""

    def propose(self, ctx: ProposalContext) -> Iterator[Proposal]:
        """Generate proposals from the search space."""
        ...

    def observe(self, record: "Record") -> None:
        """Incorporate a completed record into the policy's evidence base."""
        ...

    def get_name(self) -> str:
        """Return the policy name."""
        ...


@dataclass(frozen=True, slots=True)
class Decision:
    """Decision from S10 Decide stage."""

    transition: str  # CONTINUE | COMPLETE | PAUSE | STOP
    new_proposals: list[Proposal] = field(default_factory=list)
    promotions: list[Any] = field(default_factory=list)  # Promotion
    abandonments: list[Any] = field(default_factory=list)  # Abandonment
    replications: list[Any] = field(default_factory=list)  # Replication
    rationale: str = ""
    budget_impact: float = 0.0


@runtime_checkable
class Stage(Protocol):
    """Protocol for pipeline stages."""

    stage_id: "StageId"

    async def run(self, ctx: "StageContext") -> "Fragment":
        """Execute the stage and return a fragment."""
        ...


@dataclass(slots=True)
class StageContext:
    """Context passed to each stage during execution."""

    run_id: str
    run_spec: dict[str, Any]
    stage_id: "StageId"
    store: "RecordStore"
    budget: "Budget"
    cost_model: "CostModel"
    policy: Policy
    allocator: "EvidenceDrivenAllocator | None"
    backend: "ExecutionBackend"
    search_space: SearchSpace
    completed_keys: set[str]
    pending_proposals: list[Proposal]
    pending_candidates: list[tuple["Coordinate", "Schedule"]]
    in_progress: list[tuple["Coordinate", "Schedule"]]
    stage_params: dict[str, Any]
    provenance: Any  # Provenance
    system_context: "SystemContext"


@dataclass(frozen=True, slots=True)
class Fragment:
    """Output fragment from a stage execution."""

    stage_id: "StageId"
    records: list["Record"] = field(default_factory=list)
    proposals: list[Proposal] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    coverage: dict[str, Any] = field(default_factory=dict)
    classification: dict[str, Any] = field(default_factory=dict)
    decisions: list[Any] = field(default_factory=list)  # Decision objects


# Forward references resolved at runtime
from computronium.experiment.execution.stage import StageId  # noqa: E402
from computronium.experiment.execution.allocator import EvidenceDrivenAllocator  # noqa: E402
from computronium.experiment.execution.backends import ExecutionBackend  # noqa: E402
from computronium.experiment.execution.sysctx import SystemContext  # noqa: E402


__all__ = [
    "SearchSpace",
    "ProposalContext",
    "Proposal",
    "Policy",
    "Decision",
    "Stage",
    "StageContext",
    "Fragment",
    "Domain",
]