"""Stage definitions for the S1-S11 pipeline (WP9 — canonical model).

Canonical stages per TODO43 §3.0 / abc3 §5.1:
S1 Frame      — Objective/operating-point resolution (R43 entry, with Synthesis)
S2 Space      — Axis snapshot + legality preview (dry-run = same engine, C32)
S3 Schedule   — Fidelity/seed/epoch planning; per-task adaptation (R44)
S4 Gate       — LegalityEngine enforcement; globally-suppressive voids (R38)
S5 Compose    — compose_joint_system bridge; effective-value recording (R6)
S6 Train      — SystemTrainer settle bridge; guard/divergence telemetry (R50/R51)
S7 Measure    — Objectives resolved against OBJECTIVES; probes; robustness (R69)
S8 Record     — Atomic append + artifacts + embedding generation (vector_index)
S9 Attribute  — Counterfactual axis attribution from records (R86)
S10 Decide    — Promotion predicates + allocation handoff (R36, R46-R51)
S11 Report    — Delegates to surface.report fragments
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from enum import StrEnum
from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

if TYPE_CHECKING:
    from computronium.experiment.evidence.store import RecordStore
    from computronium.experiment.execution.allocator import EvidenceDrivenAllocator
    from computronium.experiment.execution.backends import ExecutionBackend
    from computronium.experiment.execution.budget import Budget, CostModel
    from computronium.experiment.execution.policy import Policy
    from computronium.experiment.execution.search_space import SearchSpace
    from computronium.experiment.execution.sysctx import SystemContext
    from computronium.experiment.schema.coordinate import Coordinate, Schedule
    from computronium.experiment.schema.record import Record
    from computronium.experiment.schema.run_spec import RunSpec


class StageId(StrEnum):
    """Stage identifiers for the S1-S11 pipeline per TODO43 §3.0 / abc3 §5.1."""

    S1_FRAME = "s1_frame"
    S2_SPACE = "s2_space"
    S3_SCHEDULE = "s3_schedule"
    S4_GATE = "s4_gate"
    S5_COMPOSE = "s5_compose"
    S6_TRAIN = "s6_train"
    S7_MEASURE = "s7_measure"
    S8_RECORD = "s8_record"
    S9_ATTRIBUTE = "s9_attribute"
    S10_DECIDE = "s10_decide"
    S11_REPORT = "s11_report"


class StageGate(StrEnum):
    """Gate verdicts for stage transitions."""

    PASS_ = "pass"  # ruff: ignore[hardcoded-password-string] - not a password
    FAIL = "fail"
    QUARANTINE = "quarantine"
    SKIP = "skip"


class StageTransition(StrEnum):
    """Stage transition decisions for round loop control (WP16)."""

    CONTINUE = "continue"
    COMPLETE = "complete"
    PAUSE = "pause"
    STOP = "stop"
    QUARANTINE = "quarantine"
    SKIP = "skip"


@dataclass(frozen=True, slots=True)
class Proposal:
    """One cell a policy proposed to execute, with the reason it was proposed."""

    coordinate: Coordinate
    schedule: Schedule
    rationale: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def proposal_id(self) -> str:
        """A stable identity for this proposal."""
        content = (
            f"{self.coordinate.cell_key()}|{self.schedule.fidelity}|"
            f"{self.schedule.seed}|{self.rationale}"
        )
        return hashlib.sha256(content.encode()).hexdigest()[:16]


@dataclass(frozen=True, slots=True)
class Fragment:
    """Output fragment from a stage execution.

    Each stage emits a fragment containing its specific outputs.
    Fragments are collected by the pipeline for traceability (R20).
    """

    stage_id: StageId
    records: list[Record] = field(default_factory=list)
    proposals: list[Proposal] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    coverage: dict[str, Any] = field(default_factory=dict)  # R18 coverage reporting
    classification: dict[str, Any] = field(
        default_factory=dict
    )  # R19 rejection classification
    decisions: list = field(default_factory=list)  # Decision objects from S10


@dataclass(slots=True)
class StageContext:
    """Context passed to each stage during execution."""

    run_id: str
    run_spec: RunSpec
    stage_id: StageId
    store: RecordStore
    budget: Budget
    cost_model: CostModel
    policy: Policy
    allocator: EvidenceDrivenAllocator | None
    backend: ExecutionBackend
    search_space: SearchSpace
    completed_keys: set[str]
    pending_proposals: list[Proposal]
    in_progress: list[tuple[Coordinate, Schedule]]
    stage_params: dict[str, Any]
    provenance: Any  # Provenance
    system_context: SystemContext


@runtime_checkable
class Stage(Protocol):
    """Protocol for pipeline stages.

    Each stage implements a `run` method that takes a context and returns a Fragment.
    Stages are swappable and never change the record schema (R40).
    """

    stage_id: StageId

    async def run(self, ctx: StageContext) -> Fragment:
        """Execute the stage and return a fragment.

        Args:
            ctx: Stage execution context containing run state, store, etc.

        Returns:
            Fragment with records, proposals, metadata, coverage, classification.
        """
        ...


@dataclass(frozen=True, slots=True)
class StageSpec:
    """Specification for a pipeline stage."""

    stage_id: StageId
    name: str  # Canonical stage ID (e.g., "s1_frame") - used as registry key
    display_name: str  # Human-readable name (e.g., "Frame")
    description: str = ""
    required_fidelity: str = "L1"
    min_n_seeds: int = 1
    gate: str = "pass"
    params: dict[str, Any] = field(default_factory=dict)


# S1-S11 Canonical Stage Definitions (TODO43 §3.0 / abc3 §5.1)

S1_FRAME = StageSpec(
    stage_id=StageId.S1_FRAME,
    name="s1_frame",
    display_name="Frame",
    description="Objective/operating-point resolution; question-first entry via Synthesis policy (R43)",
    required_fidelity="L0",
    min_n_seeds=1,
    gate="skip",
    params={
        "objective_resolution": True,
        "operating_points": True,
        "synthesis_policy": True,
    },
)

S2_SPACE = StageSpec(
    stage_id=StageId.S2_SPACE,
    name="s2_space",
    display_name="Space",
    description="Axis snapshot + legality preview (dry-run = same engine, C32)",
    required_fidelity="L0",
    min_n_seeds=1,
    gate="skip",
    params={
        "axis_snapshot": True,
        "legality_dry_run": True,
        "max_cells": 1000,
        "coverage_target": 0.8,
    },
)

S3_SCHEDULE = StageSpec(
    stage_id=StageId.S3_SCHEDULE,
    name="s3_schedule",
    display_name="Schedule",
    description="Fidelity/seed/epoch planning; per-task adaptation (R44); data-origin allocation + contrast quota (L19)",
    required_fidelity="L1",
    min_n_seeds=1,
    gate="pass",
    params={
        "fidelity_planning": True,
        "seed_planning": True,
        "per_task_adaptation": True,
        "data_origin_allocation": {"exploration": 0.5, "calibration": 0.3, "test": 0.2},
        "contrast_quota": 0.1,  # Fractional-factorial or OFAT within exploration budget
    },
)

S4_GATE = StageSpec(
    stage_id=StageId.S4_GATE,
    name="s4_gate",
    display_name="Gate",
    description="LegalityEngine enforcement; globally-suppressive voids (R38)",
    required_fidelity="L1",
    min_n_seeds=1,
    gate="pass",
    params={
        "legality_enforcement": True,
        "void_suppression": True,
        "apply_constraints": True,
    },
)

S5_COMPOSE = StageSpec(
    stage_id=StageId.S5_COMPOSE,
    name="s5_compose",
    display_name="Compose",
    description="compose_joint_system bridge; effective-value recording (R6)",
    required_fidelity="L1",
    min_n_seeds=1,
    gate="pass",
    params={
        "compose_joint_system": True,
        "effective_value_recording": True,
    },
)

S6_TRAIN = StageSpec(
    stage_id=StageId.S6_TRAIN,
    name="s6_train",
    display_name="Train",
    description="SystemTrainer settle bridge; guard/divergence telemetry (R50/R51); per-epoch intermediate values feed pruners",
    required_fidelity="L1",
    min_n_seeds=3,
    gate="pass",
    params={
        "system_trainer": True,
        "settle_bridge": True,
        "divergence_telemetry": True,
        "guard_telemetry": True,
        "pruner_intermediate_values": True,
    },
)

S7_MEASURE = StageSpec(
    stage_id=StageId.S7_MEASURE,
    name="s7_measure",
    display_name="Measure",
    description="Objectives resolved against OBJECTIVES; probes; robustness dimension (R69) computed when profile requests it",
    required_fidelity="L2",
    min_n_seeds=5,
    gate="pass",
    params={
        "objective_resolution": True,
        "probes": True,
        "robustness_dimension": True,
    },
)

S8_RECORD = StageSpec(
    stage_id=StageId.S8_RECORD,
    name="s8_record",
    display_name="Record",
    description="Atomic append + artifacts + embedding generation (vector_index write with embedding_version; brute-force retrieval)",
    required_fidelity="L2",
    min_n_seeds=5,
    gate="pass",
    params={
        "atomic_append": True,
        "artifacts": True,
        "embedding_generation": True,
        "vector_index_write": True,
    },
)

S9_ATTRIBUTE = StageSpec(
    stage_id=StageId.S9_ATTRIBUTE,
    name="s9_attribute",
    display_name="Attribute",
    description="Counterfactual axis attribution from records (R86)",
    required_fidelity="L2",
    min_n_seeds=1,
    gate="pass",
    params={
        "counterfactual_attribution": True,
        "axis_attribution": True,
    },
)

S10_DECIDE = StageSpec(
    stage_id=StageId.S10_DECIDE,
    name="s10_decide",
    display_name="Decide",
    description="Promotion predicates + allocation handoff (R36, R46-R51)",
    required_fidelity="L2",
    min_n_seeds=1,
    gate="pass",
    params={
        "promotion_predicates": True,
        "allocation_handoff": True,
        "evidence_driven_allocation": True,
    },
)

S11_REPORT = StageSpec(
    stage_id=StageId.S11_REPORT,
    name="s11_report",
    display_name="Report",
    description="Delegates to surface.report fragments (R85-R88)",
    required_fidelity="L2",
    min_n_seeds=1,
    gate="pass",
    params={
        "report_generation": True,
        "pareto_frontiers": True,
        "cross_run_campaign_diff": True,
    },
)

# Ordered stage list for pipeline
STAGE_SPECS: list[StageSpec] = [
    S1_FRAME,
    S2_SPACE,
    S3_SCHEDULE,
    S4_GATE,
    S5_COMPOSE,
    S6_TRAIN,
    S7_MEASURE,
    S8_RECORD,
    S9_ATTRIBUTE,
    S10_DECIDE,
    S11_REPORT,
]

STAGE_REGISTRY: dict[StageId, StageSpec] = {s.stage_id: s for s in STAGE_SPECS}


def get_stage_spec(stage_id: StageId) -> StageSpec:
    """Get stage specification by ID."""
    if stage_id not in STAGE_REGISTRY:
        raise ValueError(f"Unknown stage: {stage_id}")
    return STAGE_REGISTRY[stage_id]


def get_next_stage(stage_id: StageId) -> StageId | None:
    """Get the next stage in the pipeline."""
    idx = STAGE_SPECS.index(get_stage_spec(stage_id))
    if idx + 1 < len(STAGE_SPECS):
        return STAGE_SPECS[idx + 1].stage_id
    return None


def get_previous_stage(stage_id: StageId) -> StageId | None:
    """Get the previous stage in the pipeline."""
    idx = STAGE_SPECS.index(get_stage_spec(stage_id))
    if idx > 0:
        return STAGE_SPECS[idx - 1].stage_id
    return None


__all__ = [
    "S1_FRAME",
    "S2_SPACE",
    "S3_SCHEDULE",
    "S4_GATE",
    "S5_COMPOSE",
    "S6_TRAIN",
    "S7_MEASURE",
    "S8_RECORD",
    "S9_ATTRIBUTE",
    "S10_DECIDE",
    "S11_REPORT",
    "STAGE_REGISTRY",
    "STAGE_SPECS",
    "Fragment",
    "Proposal",
    "Stage",
    "StageContext",
    "StageGate",
    "StageId",
    "StageSpec",
    "StageTransition",
    "get_next_stage",
    "get_previous_stage",
    "get_stage_spec",
]
