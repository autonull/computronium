"""Additional registries for the experiment kernel (WP2).

Provides registry instances for OBJECTIVES, CONSTRAINTS, PRIORS, POLICIES,
STAGES, and CAPABILITIES following the same pattern as AXES_REGISTRIES.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import TYPE_CHECKING, Any, Final, TypeVar

from computronium.experiment.schema.registry import Registry

if TYPE_CHECKING:
    from computronium.experiment.legality.dsl import Expr

SpecT = TypeVar("SpecT")

# R25: a cell may exceed its declared parameter ceiling by this fraction and
# still count as fair. Declared once, because both the registered predicate and
# the evaluator's gate read it.
PARAM_BUDGET_TOLERANCE: Final[float] = 0.25

# Replay gate (TODO48 E4): a promoted cell re-measured must reproduce its
# claimed metrics within this relative tolerance to earn maturity L2.
REPLAY_METRIC_TOLERANCE: Final[float] = 0.25

# TODO48b R2: measured seconds per cell, per dynamics primitive, at the regime
# `scripts/probes/dynamics_cost.py` prices (digits, feedforward x fast_weights x
# gradient x euclidean, L0, 1 epoch, batch_limit 2, hidden_dim 64). The economy
# of a campaign is decided by which dynamics it sweeps, so the price belongs in a
# registry where the oracle, the report and the next session all read it.
MEASURED_CELL_SECONDS: Final[dict[str, float]] = {
    "energy_minimization": 0.710,
    "lazy": 0.396,
    "instantaneous": 0.084,
}

MEASURED_CELL_SECONDS_REGIME: Final[str] = (
    "digits, feedforward x fast_weights x gradient x euclidean, L0, 1 epoch, "
    "batch_limit 2, hidden_dim 64 (scripts/probes/dynamics_cost.py)"
)

# An unmeasured primitive is priced as the cheapest measured one: a number
# invented for it would be a guess wearing a decimal point's clothes.
DEFAULT_CELL_SECONDS: Final[float] = min(MEASURED_CELL_SECONDS.values())


def cell_price_seconds(dynamics: str, *, epochs: int = 1) -> float:
    """Seconds one cell of ``dynamics`` costs, scaled by its epochs.

    Args:
        dynamics: The cell's dynamics primitive.
        epochs: Epochs the cell trains; the measured regime is one.

    Returns:
        The cell's projected seconds.
    """
    base = MEASURED_CELL_SECONDS.get(dynamics, DEFAULT_CELL_SECONDS)
    return base * max(1, epochs)


@dataclass(frozen=True, slots=True)
class ObjectiveSpec:
    """Specification for an objective function.

    An objective name is not a measurement. ``metric_key`` names the payload key
    that satisfies it; without one the row is a research target awaiting a
    measurement, and it says so in ``unavailable_reason`` — the same
    recorded-reason rule an unavailable ``AxisSpec`` follows (TODO46 §D17).
    """

    name: str
    description: str = ""
    direction: str = "minimize"  # "minimize" or "maximize"
    weight: float = 1.0  # Weight in multi-objective optimization
    normalizer: str | None = None  # Normalizer function name (e.g., "minmax", "zscore")
    axis_tag: str | None = None  # Axis this objective primarily relates to
    metric_key: str | None = None  # Payload key a record carries it in
    unavailable_reason: str | None = None  # Required when metric_key is None

    def stamped(self) -> ObjectiveSpec:
        """This row carrying a measurement, or the reason it lacks one."""
        if self.metric_key is not None:
            return self
        if self.unavailable_reason:
            return self
        msg = (
            f"objective {self.name!r} declares no metric_key, so it needs an "
            "unavailable_reason: an unmeasurable objective without a recorded "
            "reason is a claim the run withdraws silently"
        )
        raise ValueError(msg)


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
    # Metadata for single-source accessor (L11)
    confidence: float = 1.0  # 0-1, confidence in this prior
    uncertainty: float = 0.0  # Uncertainty in the prior parameters
    override_scope: str = ""  # "run", "coordinate", "global" - scope for overrides


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


class CapabilityKind(StrEnum):
    """Capability categories for conformance tracking."""

    CORE = "core"
    ACCELERATION = "acceleration"
    SCALING = "scaling"
    REPRODUCIBILITY = "reproducibility"
    GOVERNANCE = "governance"
    LEARNING = "learning"


class CapabilityStatus(StrEnum):
    """Capability status for currency tracking (R78).

    ``UNVERIFIED`` is TODO46 D23's rule made representable: the capability is
    registered and may well be implemented, but the row names no test that
    exercises it, so it is not evidence of anything. A row may only hold that
    status with a recorded reason.
    """

    ACTIVE = "active"
    UNVERIFIED = "unverified"
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
    unverified_reason: str | None = None  # Why no test exercises it if UNVERIFIED

    def __post_init__(self) -> None:
        if self.name != self.capability_id:
            raise ValueError(
                f"CapabilitySpec.name ({self.name}) must equal capability_id ({self.capability_id})"
            )
        if self.status is CapabilityStatus.UNVERIFIED and not self.unverified_reason:
            raise ValueError(
                f"CapabilitySpec({self.capability_id}) is UNVERIFIED without a reason"
            )
        if self.status is CapabilityStatus.RETIRED and not self.retirement_record:
            raise ValueError(
                f"CapabilitySpec({self.capability_id}) is RETIRED without a retirement record"
            )


# Registry instances
OBJECTIVES_REGISTRY: Registry[ObjectiveSpec] = Registry[ObjectiveSpec]()
CONSTRAINTS_REGISTRY: Registry[ConstraintSpec] = Registry[ConstraintSpec]()
PRIORS_REGISTRY: Registry[PriorSpec] = Registry[PriorSpec]()
POLICIES_REGISTRY: Registry[PolicySpec] = Registry[PolicySpec]()
STAGES_REGISTRY: Registry[StageSpec] = Registry[StageSpec]()
CAPABILITIES_REGISTRY: Registry[CapabilitySpec] = Registry[CapabilitySpec]()

# Card factors: soft priors for (credit, update) pairs used by synthesis engine.
# (credit, update) -> (factor: float, verdict: str | None)
CARD_FACTORS: dict[tuple[str, str], tuple[float, str | None]] = {}


def register_card_factor(
    credit: str, update: str, factor: float, verdict: str | None = None
) -> None:
    """Register a card factor for a (credit, update) pair."""
    CARD_FACTORS[credit, update] = (factor, verdict)


def get_card_factor(credit: str, update: str) -> tuple[float, str | None]:
    """Get card factor for a (credit, update) pair; neutral default if unknown."""
    return CARD_FACTORS.get((credit, update), (1.0, None))


# Register default card factors (credit, update) -> (factor, verdict).
# These are soft priors; factor > 1.0 favors the pair, < 1.0 disfavors.
# Verdict is a human-readable label (e.g., "canonical", "experimental").
def _register_default_card_factors() -> None:
    # Canonical pairs (well-tested combinations)
    register_card_factor("Backprop", "Euclidean", 1.0, "canonical")
    register_card_factor("EquilibriumProp", "Euclidean", 1.0, "canonical")
    register_card_factor("PredictiveCoding", "Euclidean", 1.0, "canonical")
    register_card_factor("LocalGoodness", "Euclidean", 1.0, "canonical")
    register_card_factor("Hebbian", "Euclidean", 1.0, "canonical")
    register_card_factor("TargetProp", "Euclidean", 1.0, "canonical")

    # Energy-minimizing dynamics + local credit
    register_card_factor("LocalGoodness", "Euclidean", 1.2, "energy_local")
    register_card_factor("ThermodynamicContrast", "Euclidean", 1.1, "energy_local")
    register_card_factor("Homeostatic", "Euclidean", 1.1, "energy_local")
    register_card_factor("Pepita", "Euclidean", 1.1, "energy_local")
    register_card_factor("SpectralConstrained", "Euclidean", 1.1, "energy_local")

    # Diffusion dynamics + temporal credit
    register_card_factor("TemporalTrace", "Euclidean", 1.2, "diffusion_temporal")
    register_card_factor("TemporalTrace", "Adam", 1.1, "diffusion_temporal")

    # Predictive settling + contrastive credit
    register_card_factor("LocalContrastive", "Euclidean", 1.1, "predictive_contrastive")


_register_default_card_factors()


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
    """Register an objective specification.

    Raises:
        ValueError: The row is unmeasured and records no reason. Registration is
            where the rule bites, because that is where a run can start
            searching on it.
    """
    OBJECTIVES_REGISTRY.register(spec.stamped())


def register_constraint(spec: ConstraintSpec) -> None:
    """Register a constraint specification."""
    CONSTRAINTS_REGISTRY.register(spec)


def register_prior(spec: PriorSpec) -> None:
    """Register a prior specification."""
    PRIORS_REGISTRY.register(spec)


def prior_value(
    name: str,
    context: dict[str, Any] | None = None,
) -> tuple[float, float, float] | None:
    """Get a prior value with confidence and uncertainty (single-source accessor, L11).

    Args:
        name: The prior name (e.g., "lr_ruler_mnist", "step_size_energy_minimization_backprop").
        context: Optional context for per-run/per-coordinate overrides.
            Keys: "run_id", "coordinate", "override" (dict of param overrides).

    Returns:
        Tuple of (center_value, confidence, uncertainty) or None if not found.
        For log_uniform distributions, center is the geometric mean.
        For normal distributions, center is the mean.
        For categorical, center is the first choice.
    """
    prior = PRIORS_REGISTRY.get(name)
    if prior is None:
        return None

    # Extract center value from distribution params
    center = _extract_prior_center(prior.distribution, prior.params)

    # Apply context overrides if provided
    if context and context.get("override"):
        override_params = context["override"]
        if name in override_params:
            override = override_params[name]
            if isinstance(override, int | float):
                center = float(override)
            elif isinstance(override, dict) and "center" in override:
                center = float(override["center"])

    return (center, prior.confidence, prior.uncertainty)


def _extract_prior_center(distribution: str, params: dict) -> float:
    """Extract the center/mean value from distribution parameters."""
    match distribution:
        case "log_uniform":
            # Geometric mean of low and high
            low = params.get("low", 1e-3)
            high = params.get("high", 1.0)
            center = params.get("center", (low * high) ** 0.5)
            return float(center)
        case "normal" | "log_normal":
            return float(params.get("mean", params.get("center", 0.0)))
        case "uniform":
            low = params.get("low", 0.0)
            high = params.get("high", 1.0)
            return float(params.get("center", (low + high) / 2))
        case "categorical":
            choices = params.get("choices", [])
            return float(choices[0]) if choices else 0.0
        case _:
            return float(params.get("center", params.get("mean", 0.0)))


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
    "CARD_FACTORS",
    "CONSTRAINTS_REGISTRY",
    "DEFAULT_CELL_SECONDS",
    "MEASURED_CELL_SECONDS",
    "MEASURED_CELL_SECONDS_REGIME",
    "OBJECTIVES_REGISTRY",
    "PARAM_BUDGET_TOLERANCE",
    "POLICIES_REGISTRY",
    "PRIORS_REGISTRY",
    "REPLAY_METRIC_TOLERANCE",
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
    "cell_price_seconds",
    "get_card_factor",
    "prior_value",
    "register_capability",
    "register_card_factor",
    "register_constraint",
    "register_objective",
    "register_policy",
    "register_prior",
    "register_stage",
]
