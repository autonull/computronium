"""Pipeline configuration, state and small pure helpers."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Final

from computronium.experiment.execution.deadline import (
    CellTiming,
    Deadline,
    DeadlineEnforcer,
    SignalHandler,
)
from computronium.experiment.execution.stage import Proposal, StageId
from computronium.experiment.schema.coordinate import (
    Coordinate,
    DataOrigin,
    Provenance,
    Schedule,
)

# The stages one round walks, in order. The order is the pipeline's meaning —
# schedule, gate, compose, train, measure, record, attribute, decide — and a
# stage the run does not declare is skipped rather than reordered.
_ROUND_STAGE_ORDER: Final = (
    StageId.S3_SCHEDULE,
    StageId.S4_GATE,
    StageId.S5_COMPOSE,
    StageId.S6_TRAIN,
    StageId.S7_MEASURE,
    StageId.S8_RECORD,
    StageId.S9_ATTRIBUTE,
    StageId.S10_DECIDE,
)

if TYPE_CHECKING:
    from pathlib import Path

    from computronium.experiment.execution.allocator import EvidenceDrivenAllocator
    from computronium.experiment.execution.backends import ExecutionBackend
    from computronium.experiment.execution.decision import Decision, RoundController
    from computronium.experiment.execution.policy import Policy
    from computronium.experiment.execution.stream import CellStream, CellStreamState
    from computronium.experiment.execution.sysctx import SystemContext
    from computronium.experiment.kernel.resources import CostModel
    from computronium.experiment.kernel.search_space import SearchSpace
    from computronium.experiment.schema.run_spec import RunSpec


class ZeroYieldError(RuntimeError):
    """Raised when K>=3 consecutive batches produce zero successes with a
    single shared failure cause. This is a reviewable failure, not a silent stop.
    """

    def __init__(self, cause: str, count: int, message: str):
        super().__init__(
            f"ZeroYieldError: {count} consecutive batches failed with cause '{cause}': {message}"
        )
        self.cause = cause
        self.count = count


@dataclass(frozen=True, slots=True)
class PipelineConfig:
    """Configuration for the pipeline runner."""

    run_id: str
    run_spec: RunSpec
    stages: list[StageId] = field(default_factory=list)
    deadline: Deadline | None = None  # Hard deadline (replaces budget)
    budget: Any = (
        None  # Backward compatibility: accepts legacy Budget, converts to deadline
    )
    # Cells this launch may measure before stopping. Read from the legacy
    # Budget's ``target_cells``; a per-launch cap, so a resume continues.
    session_cell_limit: int | None = None
    cost_model: CostModel | None = None
    policy: Policy | None = None
    allocator: EvidenceDrivenAllocator | None = None
    backend: ExecutionBackend | None = None
    max_concurrent_evaluations: int = 10
    seed: int | None = None
    # Task IDs for multi-task runs (L17)
    task_ids: list[str] = field(default_factory=list)
    # Round controller config
    max_rounds: int | None = None
    min_rounds: int = 1
    # Runtime provenance (WP19)
    dtype: str = "float32"
    worker_config: dict[str, Any] = field(default_factory=dict)
    code_sha: str = "unknown"
    # The control plane this run reads. Derived from the store's path by
    # ``control_plane_path`` so the dashboard and the run cannot disagree
    # about where the control channel lives (TODO70).
    control_plane: Path | None = None

    def __post_init__(self) -> None:
        # Convert legacy Budget to Deadline if provided, and carry its
        # per-launch cell cap. ``dataclasses.replace`` re-runs this even when a
        # deadline is already present, so the cap cannot depend on conversion.
        if self.budget is not None:
            from computronium.experiment.execution.deadline import Deadline
            from computronium.experiment.kernel.resources import Budget as LegacyBudget

            if isinstance(self.budget, LegacyBudget):
                object.__setattr__(self, "session_cell_limit", self.budget.target_cells)
                if self.deadline is None:
                    object.__setattr__(
                        self,
                        "deadline",
                        Deadline.from_seconds(self.budget.soft_seconds or 3600),
                    )


def _resolve_tasks(config: PipelineConfig) -> tuple[str, ...]:
    """The run's task names: the spec's, unless the config overrides them.

    ``RunSpec`` already refused an unresolvable task, so an empty result means
    the run measured nothing and the override must be checked here.
    """
    names = tuple(config.task_ids) or config.run_spec.task_names
    if not names:
        msg = f"run {config.run_id} names no task"
        raise ValueError(msg)
    from computronium.domains.registry import SUPPORTED_TASKS

    unknown = [n for n in names if n not in SUPPORTED_TASKS]
    if unknown:
        msg = f"unknown task(s) {unknown}; available: {sorted(SUPPORTED_TASKS)}"
        raise ValueError(msg)
    return names


_CONTRAST_LINK_KEYS: Final = ("contrast_id", "matched_group", "factor_assignments")


def _provenance_for(provenance: Provenance, proposal: Proposal) -> Provenance:
    """The run's provenance as this proposal's own record will carry it.

    ``data_origin`` is the schema's own field for the S1 allocation and the
    contrast design's group; the design's identifiers ride in ``links`` beside
    ``run_id``. Identity is untouched — the schedule is unchanged, so the same
    cell under two origins is still the same measurement key.
    """
    from dataclasses import replace

    metadata = proposal.metadata
    links = dict(provenance.links)
    for key in _CONTRAST_LINK_KEYS:
        if key in metadata:
            links[key] = str(metadata[key])
    if not links.keys() - {"run_id"} and provenance.data_origin == metadata.get(
        "data_origin", provenance.data_origin
    ):
        return provenance
    return replace(
        provenance,
        data_origin=DataOrigin(metadata.get("data_origin", provenance.data_origin)),
        links=links,
    )


@dataclass(slots=True)
class PipelineState:
    """Mutable state for pipeline execution."""

    run_id: str
    current_stage_idx: int = 0
    current_round: int = 0
    completed_measurement_keys: set[str] = field(default_factory=set)
    pending_proposals: list[Proposal] = field(default_factory=list)
    in_progress: list[tuple[Coordinate, Schedule]] = field(default_factory=list)
    deadline: Deadline | None = None
    deadline_enforcer: DeadlineEnforcer | None = None
    cell_timing: CellTiming = field(default_factory=CellTiming)
    signal_handler: SignalHandler | None = None
    allocator_state: dict[str, Any] | None = None
    allocator_promotions: list[tuple[Coordinate, Schedule]] = field(
        default_factory=list
    )
    last_decision: Decision | None = None
    # Coverage tracking (R18)
    coverage: dict[str, Any] = field(default_factory=dict)
    # Rejection classification (R19)
    rejections: list[dict[str, Any]] = field(default_factory=list)
    # Proposal provenance (R20)
    proposal_provenance: list[dict[str, Any]] = field(default_factory=list)
    # Replay hash tracking (R26/R27)
    replay_hash: str | None = None
    # Round controller
    round_controller: RoundController | None = None
    # Search space
    search_space: SearchSpace | None = None
    # Admission gate: durable set of rejected keys (never re-proposed)
    rejected_keys: set[str] = field(default_factory=set)
    # Batch sizer for budget-aware n_propose
    batch_sizer: Any = None  # BatchSizer, imported locally to avoid cycle
    # Cell stream for unbounded candidate generation
    cell_stream: CellStream | None = None
    cell_stream_state: CellStreamState | None = None
    # Consecutive zero-yield batches for ZeroYieldError
    zero_yield_count: int = 0
    last_zero_yield_cause: str | None = None
    # System context with environment snapshot (WP19/R75/K10)
    system_context: SystemContext | None = None
    # Last measured duration per stage, stamped into every record payload
    stage_timings: dict[str, float] = field(default_factory=dict)
    # The stage the run is in, by its own name: what the dashboard reads.
    current_stage: str = ""
