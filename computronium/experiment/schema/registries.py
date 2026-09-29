"""Additional registries for the experiment kernel (WP2).

Provides registry instances for OBJECTIVES, CONSTRAINTS, PRIORS, POLICIES,
STAGES, and CAPABILITIES following the same pattern as AXES_REGISTRIES.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import TypeVar

from computronium.experiment.schema.registry import Registry

SpecT = TypeVar("SpecT")


@dataclass(frozen=True, slots=True)
class ObjectiveSpec:
    """Specification for an objective function."""

    name: str
    description: str = ""
    direction: str = "minimize"  # "minimize" or "maximize"


@dataclass(frozen=True, slots=True)
class ConstraintSpec:
    """Specification for a constraint."""

    name: str
    kind: str  # "hard", "soft", "budget"
    description: str = ""
    params: dict | None = None


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


@dataclass(frozen=True, slots=True)
class CapabilitySpec:
    """Specification for a capability (for conformance registry)."""

    capability_id: str
    kind: CapabilityKind
    name: str
    description: str = ""
    required: bool = True
    gated_by: str | None = None  # Gate that enables this capability


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
    "ConstraintSpec",
    "ObjectiveSpec",
    "PolicyKind",
    "PolicySpec",
    "PriorSpec",
    "StageId",
    "StageSpec",
    "register_capability",
    "register_constraint",
    "register_objective",
    "register_policy",
    "register_prior",
    "register_stage",
]
