"""Stage definitions for the S1-S11 pipeline (WP4)."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from computronium.experiment.schema.coordinate import Coordinate, Schedule
    from computronium.experiment.schema.record import Record


class StageId(StrEnum):
    """Stage identifiers for the S1-S11 pipeline."""

    S1_DISCOVERY = "s1_discovery"
    S2_VALIDATION = "s2_validation"
    S3_CALIBRATION = "s3_calibration"
    S4_EXPANSION = "s4_expansion"
    S5_MATURATION = "s5_maturation"
    S6_CLAIM = "s6_claim"
    S7_REPRODUCTION = "s7_reproduction"
    S8_DISTILLATION = "s8_distillation"
    S9_DEPLOYMENT = "s9_deployment"
    S10_MONITORING = "s10_monitoring"
    S11_RETIREMENT = "s11_retirement"


class StageGate(StrEnum):
    """Gate verdicts for stage transitions."""

    PASS = "pass"  # noqa: S105 - not a password
    FAIL = "fail"
    QUARANTINE = "quarantine"
    SKIP = "skip"


@dataclass(frozen=True, slots=True)
class StageSpec:
    """Specification for a pipeline stage."""

    stage_id: StageId
    name: str
    description: str = ""
    required_fidelity: str = "L1"
    min_n_seeds: int = 1
    gate: str = "pass"
    # Stage-specific parameters
    params: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class StageResult:
    """Result of executing a stage."""

    stage_id: StageId
    gate_verdict: StageGate
    records: list[Record]
    proposals: list[tuple[Coordinate, Schedule]]  # Candidates for next stage
    metadata: dict[str, Any] = field(default_factory=dict)


# S1-S11 Stage Definitions (abc3 §5.2)

S1_DISCOVERY = StageSpec(
    stage_id=StageId.S1_DISCOVERY,
    name="Discovery",
    description="Initial broad mapping of the 6-axis space at low fidelity (L0)",
    required_fidelity="L0",
    min_n_seeds=1,
    gate="pass",
    params={
        "max_cells": 1000,
        "coverage_target": 0.8,  # Fraction of axis combinations to cover
        "fidelity": "L0",
    },
)

S2_VALIDATION = StageSpec(
    stage_id=StageId.S2_VALIDATION,
    name="Validation",
    description="Validate promising cells from S1 at medium fidelity (L1)",
    required_fidelity="L1",
    min_n_seeds=3,
    gate="pass",
    params={
        "promotion_threshold": 0.1,
        "max_cells": 200,
        "fidelity": "L1",
    },
)

S3_CALIBRATION = StageSpec(
    stage_id=StageId.S3_CALIBRATION,
    name="Calibration",
    description="Calibrate hyperparameters for promoted cells using evidence-driven allocation",
    required_fidelity="L1",
    min_n_seeds=5,
    gate="pass",
    params={
        "cost_budget_fraction": 0.3,
        "max_cells": 100,
        "fidelity": "L1",
    },
)

S4_EXPANSION = StageSpec(
    stage_id=StageId.S4_EXPANSION,
    name="Expansion",
    description="Expand search around calibrated cells; apply legality constraints (S4/S6 enforcement)",
    required_fidelity="L1",
    min_n_seeds=3,
    gate="pass",
    params={
        "expansion_radius": 1,
        "max_cells": 300,
        "fidelity": "L1",
        "apply_constraints": True,
    },
)

S5_MATURATION = StageSpec(
    stage_id=StageId.S5_MATURATION,
    name="Maturation",
    description="Mature top cells to high fidelity (L2) with full seed repetition",
    required_fidelity="L2",
    min_n_seeds=5,
    gate="pass",
    params={
        "max_cells": 50,
        "fidelity": "L2",
        "n_seeds": 5,
    },
)

S6_CLAIM = StageSpec(
    stage_id=StageId.S6_CLAIM,
    name="Claim",
    description="Claim-grade evaluation: matched-cost comparison, statistical validation",
    required_fidelity="L2",
    min_n_seeds=10,
    gate="claim",
    params={
        "max_cells": 20,
        "fidelity": "L2",
        "n_seeds": 10,
        "matched_cost": True,
        "effect_size_threshold": 0.2,  # Cohen's d
    },
)

S7_REPRODUCTION = StageSpec(
    stage_id=StageId.S7_REPRODUCTION,
    name="Reproduction",
    description="Independent reproduction across seeds, environments, and held-out tasks",
    required_fidelity="L2",
    min_n_seeds=5,
    gate="pass",
    params={
        "max_cells": 10,
        "fidelity": "L2",
        "n_seeds": 5,
        "independent_envs": True,
        "held_out_tasks": True,
    },
)

S8_DISTILLATION = StageSpec(
    stage_id=StageId.S8_DISTILLATION,
    name="Distillation",
    description="Distill findings into surrogate models and transferable priors",
    required_fidelity="L2",
    min_n_seeds=1,
    gate="pass",
    params={
        "max_cells": 5,
        "fidelity": "L2",
        "build_surrogate": True,
        "extract_priors": True,
    },
)

S9_DEPLOYMENT = StageSpec(
    stage_id=StageId.S9_DEPLOYMENT,
    name="Deployment",
    description="Deploy validated configuration to production environment",
    required_fidelity="L2",
    min_n_seeds=1,
    gate="pass",
    params={
        "max_cells": 1,
        "fidelity": "L2",
        "deployment_checklist": True,
    },
)

S10_MONITORING = StageSpec(
    stage_id=StageId.S10_MONITORING,
    name="Monitoring",
    description="Monitor deployed configuration for drift and degradation",
    required_fidelity="L2",
    min_n_seeds=1,
    gate="pass",
    params={
        "max_cells": 1,
        "fidelity": "L2",
        "monitoring_interval_hours": 24,
    },
)

S11_RETIREMENT = StageSpec(
    stage_id=StageId.S11_RETIREMENT,
    name="Retirement",
    description="Retire configuration; archive records and artifacts",
    required_fidelity="L2",
    min_n_seeds=1,
    gate="pass",
    params={
        "max_cells": 1,
        "fidelity": "L2",
        "archive_artifacts": True,
    },
)

# Ordered stage list for pipeline
STAGE_SPECS: list[StageSpec] = [
    S1_DISCOVERY,
    S2_VALIDATION,
    S3_CALIBRATION,
    S4_EXPANSION,
    S5_MATURATION,
    S6_CLAIM,
    S7_REPRODUCTION,
    S8_DISTILLATION,
    S9_DEPLOYMENT,
    S10_MONITORING,
    S11_RETIREMENT,
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
    "S1_DISCOVERY",
    "S2_VALIDATION",
    "S3_CALIBRATION",
    "S4_EXPANSION",
    "S5_MATURATION",
    "S6_CLAIM",
    "S7_REPRODUCTION",
    "S8_DISTILLATION",
    "S9_DEPLOYMENT",
    "S10_MONITORING",
    "S11_RETIREMENT",
    "STAGE_REGISTRY",
    "STAGE_SPECS",
    "StageGate",
    "StageId",
    "StageResult",
    "StageSpec",
    "get_next_stage",
    "get_previous_stage",
    "get_stage_spec",
]
