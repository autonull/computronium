"""Additional registries for the experiment kernel (WP2).

Provides registry instances for OBJECTIVES, CONSTRAINTS, PRIORS, POLICIES,
STAGES, and CAPABILITIES following the same pattern as AXES_REGISTRIES.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import TYPE_CHECKING, TypeVar

from computronium.experiment.schema.registry import Registry

if TYPE_CHECKING:
    from computronium.experiment.legality.dsl import Expr

SpecT = TypeVar("SpecT")


@dataclass(frozen=True, slots=True)
class ObjectiveSpec:
    """Specification for an objective function."""

    name: str
    description: str = ""
    direction: str = "minimize"  # "minimize" or "maximize"
    weight: float = 1.0  # Weight in multi-objective optimization
    normalizer: str | None = None  # Normalizer function name (e.g., "minmax", "zscore")
    axis_tag: str | None = None  # Axis this objective primarily relates to


class ConstraintKind(StrEnum):
    """Constraint kinds for enforcement semantics."""

    VOID = "void"  # Logically infeasible — globally suppressive (S4)
    HARD = "hard"  # Resource/budget limits — enforced at S4/S6
    SOFT = "soft"  # Preferences — encoded in PRIORS, not enforced
    FAIRNESS = "fairness"  # Param-budget tolerance (R25)
    OPERATING_POINT = "operating_point"  # Operating point constraints (R66)


class ProofKind(StrEnum):
    """Machine-checkable proof kinds for DECLARED constraints."""

    TYPE_MISMATCH = "type_mismatch"
    RESOURCE = "resource"
    LOGICAL = "logical"


@dataclass(frozen=True, slots=True)
class ConstraintSpec:
    """Specification for a constraint."""

    name: str
    kind: ConstraintKind
    description: str = ""
    params: dict | None = None
    predicate: Expr | None = None  # Expr predicate for machine-checkable evaluation
    proof_kind: ProofKind | None = None  # Proof kind for DECLARED constraints
    origin: str = "DECLARED"  # "DECLARED" | "TASK_FENCE" | "APPLY_CONSTRAINTS"


@dataclass(frozen=True, slots=True)
class PriorSpec:
    """Specification for a prior distribution."""

    name: str
    distribution: str  # "normal", "log_uniform", "categorical", etc.
    params: dict
    description: str = ""


class PolicyKind(StrEnum):
    """Kinds of allocation policies."""

    STRATIFIED_RANDOM = "stratified_random"
    ROUND_ROBIN_GRID = "round_robin_grid"
    UNIFORM_RANDOM = "uniform_random"
    MODEL_BASED = "model_based"
    EVOLUTION = "evolution"
    SYNTHESIS = "synthesis"
    STRATEGY_PROGRESSION = "strategy_progression"
    TRAINER_DRIVEN = "trainer_driven"


@dataclass(frozen=True, slots=True)
class PolicySpec:
    """Specification for an allocation policy."""

    name: str
    kind: PolicyKind
    description: str = ""
    params: dict | None = None


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


@dataclass(frozen=True, slots=True)
class StageSpec:
    """Specification for a pipeline stage."""

    stage_id: StageId
    name: str
    description: str = ""
    required_fidelity: str = "L1"
    min_n_seeds: int = 1
    gate: str = "pass"


class CapabilityKind(StrEnum):
    """Capability categories for conformance tracking."""

    CORE = "core"
    ACCELERATION = "acceleration"
    SCALING = "scaling"
    REPRODUCIBILITY = "reproducibility"
    GOVERNANCE = "governance"
    LEARNING = "learning"


class CapabilityStatus(StrEnum):
    """Capability status for currency tracking (R78)."""

    ACTIVE = "active"
    RETIRED = "retired"


@dataclass(frozen=True, slots=True)
class CapabilitySpec:
    """Specification for a capability (for conformance registry).

    The `name` field is used as the registry key and must equal `capability_id`
    (e.g., "C1", "C2", ..., "C88") for consistent lookup.
    """

    capability_id: str
    name: str  # Registry key; must equal capability_id
    kind: CapabilityKind
    display_name: str  # Human-readable name
    description: str = ""
    required: bool = True
    gated_by: str | None = None  # Gate that enables this capability
    stage: str | None = None  # Pipeline stage this capability belongs to
    owner: str | None = None  # Component owner (e.g., "pipeline", "store", "learning")
    verifying_test: str | None = None  # pytest node id of the verifying test
    flags: tuple[str, ...] = ()  # Appendix-A flags (e.g., "experimental", "gpu_only")
    status: CapabilityStatus = CapabilityStatus.ACTIVE
    retirement_record: str | None = None  # Reference to retirement record if RETIRED

    def __post_init__(self) -> None:
        if self.name != self.capability_id:
            raise ValueError(
                f"CapabilitySpec.name ({self.name}) must equal capability_id ({self.capability_id})"
            )


# Registry instances
OBJECTIVES_REGISTRY: Registry[ObjectiveSpec] = Registry[ObjectiveSpec]()
CONSTRAINTS_REGISTRY: Registry[ConstraintSpec] = Registry[ConstraintSpec]()
PRIORS_REGISTRY: Registry[PriorSpec] = Registry[PriorSpec]()
POLICIES_REGISTRY: Registry[PolicySpec] = Registry[PolicySpec]()
STAGES_REGISTRY: Registry[StageSpec] = Registry[StageSpec]()
CAPABILITIES_REGISTRY: Registry[CapabilitySpec] = Registry[CapabilitySpec]()

# Convenience exports
ALL_REGISTRIES = {
    "objectives": OBJECTIVES_REGISTRY,
    "constraints": CONSTRAINTS_REGISTRY,
    "priors": PRIORS_REGISTRY,
    "policies": POLICIES_REGISTRY,
    "stages": STAGES_REGISTRY,
    "capabilities": CAPABILITIES_REGISTRY,
}


def register_objective(spec: ObjectiveSpec) -> None:
    """Register an objective specification."""
    OBJECTIVES_REGISTRY.register(spec)


def register_constraint(spec: ConstraintSpec) -> None:
    """Register a constraint specification."""
    CONSTRAINTS_REGISTRY.register(spec)


def register_prior(spec: PriorSpec) -> None:
    """Register a prior specification."""
    PRIORS_REGISTRY.register(spec)


def register_policy(spec: PolicySpec) -> None:
    """Register a policy specification."""
    POLICIES_REGISTRY.register(spec)


def register_stage(spec: StageSpec) -> None:
    """Register a stage specification."""
    STAGES_REGISTRY.register(spec)


def register_capability(spec: CapabilitySpec) -> None:
    """Register a capability specification."""
    CAPABILITIES_REGISTRY.register(spec)


__all__ = [
    "ALL_REGISTRIES",
    "CAPABILITIES_REGISTRY",
    "CONSTRAINTS_REGISTRY",
    "OBJECTIVES_REGISTRY",
    "POLICIES_REGISTRY",
    "PRIORS_REGISTRY",
    "STAGES_REGISTRY",
    "CapabilityKind",
    "CapabilitySpec",
    "CapabilityStatus",
    "ConstraintKind",
    "ConstraintSpec",
    "ObjectiveSpec",
    "PolicyKind",
    "PolicySpec",
    "PriorSpec",
    "ProofKind",
    "StageId",
    "StageSpec",
    "register_capability",
    "register_constraint",
    "register_objective",
    "register_policy",
    "register_prior",
    "register_stage",
]
