"""CEEC-Core object models.

Frozen Pydantic models persisted to the SQLite ledger. Belief probability is
kept strictly separate from goal utility; both flow through revisions.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from ceec.ids import validate_id

EvidenceKind = Literal[
    "scalar",
    "interval",
    "vector",
    "tensor",
    "curve",
    "event",
    "distribution",
    "frontier",
    "inert",
    "missing",
]

BeliefType = Literal["instrument", "mechanism", "generality", "defect"]
BeliefStatus = Literal["open", "promoted", "boundary", "quarantined"]
Uncertainty = Literal["low", "medium", "high"]
Weight = Literal["none", "low", "medium", "high"]
Generality = Literal["narrow", "moderate", "broad", "universal"]
GoalKind = Literal["science", "program", "resource", "hygiene"]
GoalStatus = Literal["active", "blocked", "satisfied", "retired"]
ExperimentStatus = Literal["draft", "pre_registered", "running", "completed", "failed"]
GateStatus = Literal["pass", "fail", "not_evaluated"]

STRUCTURED_KINDS: frozenset[str] = frozenset({
    "vector",
    "tensor",
    "curve",
    "event",
    "distribution",
    "frontier",
})

_UNSTRUCTURED = (
    "kind {kind!r} is structured; primary evidence must carry axes and values_ref"
)


class _Frozen(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class Probability(_Frozen):
    low: float = Field(ge=0.0, le=1.0)
    high: float = Field(ge=0.0, le=1.0)
    point: float | None = Field(default=None, ge=0.0, le=1.0)
    method: str | None = None

    @model_validator(mode="after")
    def _ordered(self) -> Probability:
        if self.low > self.high:
            raise ValueError(
                f"probability interval inverted: [{self.low}, {self.high}]"
            )
        if self.point is not None and not (self.low <= self.point <= self.high):
            raise ValueError("point estimate outside interval")
        return self


class Scope(_Frozen):
    domain: str
    substrate: tuple[str, ...] = ()
    geometry: tuple[str, ...] = ()
    credit: tuple[str, ...] = ()
    budget: str | None = None
    code_commit: str | None = None
    extra: dict[str, Any] = Field(default_factory=dict)


class Artifact(_Frozen):
    id: str
    sha256: str
    uri: str
    type: str
    provenance: dict[str, Any]
    created_at: str

    def model_post_init(self, _) -> None:
        validate_id(self.id, "A")


class Evidence(_Frozen):
    id: str
    kind: EvidenceKind
    scope: Scope
    axes: list[str] | None = None
    values_ref: str | None = None
    uncertainties: dict[str, Any] | None = None
    quality: dict[str, Any] = Field(default_factory=dict)
    defects: list[str] = Field(default_factory=list)
    notes: str | None = None
    no_artifact_justification: str | None = None
    created_at: str

    def model_post_init(self, _) -> None:
        validate_id(self.id, "E")

    @model_validator(mode="after")
    def _structured(self) -> Evidence:
        if self.kind in STRUCTURED_KINDS and not (self.axes and self.values_ref):
            raise ValueError(_UNSTRUCTURED.format(kind=self.kind))
        if self.kind in {"inert", "missing"} and not self.notes:
            raise ValueError(f"{self.kind} evidence requires explanatory notes")
        return self


class Derived(_Frozen):
    id: str
    type: str
    operator: str
    inputs: dict[str, list[str]]
    left: str | None = None
    right: str | None = None
    parameters: dict[str, Any] | None = None
    value: Any = None
    probability_positive: Probability | None = None
    probability_material: Probability | None = None
    assumptions: list[str] = Field(default_factory=list)
    checks: list[str] = Field(default_factory=list)
    scope: Scope
    provenance: dict[str, Any] | None = None
    created_at: str

    def model_post_init(self, _) -> None:
        validate_id(self.id, "D")


class Belief(_Frozen):
    id: str
    statement: str
    type: BeliefType
    scope: Scope
    posterior_method: str | None = None
    created_at: str

    def model_post_init(self, _) -> None:
        validate_id(self.id, "B", "I")


class BeliefRevision(_Frozen):
    id: str
    belief_id: str
    probability: Probability
    uncertainty: Uncertainty
    evidence_weight: Weight
    generality: Generality
    status: BeliefStatus
    rationale: str
    created_at: str

    def model_post_init(self, _) -> None:
        validate_id(self.id, "BR")


class Goal(_Frozen):
    id: str
    statement: str
    kind: GoalKind
    created_at: str

    def model_post_init(self, _) -> None:
        validate_id(self.id, "G")


class GoalRevision(_Frozen):
    id: str
    goal_id: str
    utility: dict[str, float]
    scalar_utility: float | None = None
    cost_low: float | None = None
    cost_high: float | None = None
    priority: float | None = None
    status: GoalStatus = "active"
    rationale: str | None = None
    created_at: str

    def model_post_init(self, _) -> None:
        validate_id(self.id, "GR")


class Experiment(_Frozen):
    id: str
    question: str
    rationale: str
    scope: Scope
    target_beliefs: list[str]
    target_goals: list[str]
    design: dict[str, Any]
    prediction: str
    prediction_probability: Probability | None = None
    controls: list[str]
    metrics: list[str]
    budget: Literal["quick", "standard", "nightly"]
    cost_low: float | None = None
    cost_high: float | None = None
    falsification_criterion: str
    overturn_criterion: str
    hard_gates: list[str]
    status: ExperimentStatus = "draft"
    created_at: str

    def model_post_init(self, _) -> None:
        validate_id(self.id, "X")


class Decision(_Frozen):
    id: str
    timestamp: str
    state_hash: str
    candidate_experiments: list[str]
    scores: dict[str, float]
    selected_experiment: str | None
    overrides: list[dict[str, Any]] = Field(default_factory=list)
    constraints_checked: dict[str, Any] = Field(default_factory=dict)
    rationale: str

    def model_post_init(self, _) -> None:
        validate_id(self.id, "DEC")


class GateOutcome(_Frozen):
    id: str
    gate: str
    status: GateStatus
    evidence_refs: list[str] = Field(default_factory=list)
    derived_refs: list[str] = Field(default_factory=list)
    rationale: str
    belief_id: str | None = None
    experiment_id: str | None = None
    created_at: str

    def model_post_init(self, _) -> None:
        validate_id(self.id, "GO")


class StatusChange(_Frozen):
    id: str
    belief_id: str
    from_status: BeliefStatus
    to_status: BeliefStatus
    reason: str
    trigger: str | None = None
    gate_refs: list[str] = Field(default_factory=list)
    evidence_refs: list[str] = Field(default_factory=list)
    derived_refs: list[str] = Field(default_factory=list)
    actor: str | None = None
    created_at: str

    def model_post_init(self, _) -> None:
        validate_id(self.id, "SC")
        if self.to_status in {"promoted", "boundary"} and not self.gate_refs:
            raise ValueError("status change to promoted/boundary requires gate refs")
        if (
            self.to_status == "open"
            and self.from_status == "boundary"
            and not self.trigger
        ):
            raise ValueError("reopening a boundary belief requires a trigger")


class CalibrationRecord(_Frozen):
    id: str
    experiment_id: str | None = None
    belief_id: str | None = None
    prediction: str
    predicted_probability: Probability | None = None
    outcome: str | None = None
    outcome_boolean: bool | None = None
    brier_score: float | None = None
    log_score: float | None = None
    scope: Scope | None = None
    notes: str | None = None
    created_at: str

    def model_post_init(self, _) -> None:
        validate_id(self.id, "CAL")

    @model_validator(mode="after")
    def _scores(self) -> CalibrationRecord:
        if self.brier_score is not None and self.predicted_probability is None:
            raise ValueError("Brier score requires a declared point probability")
        if self.outcome_boolean is not None and self.predicted_probability is None:
            raise ValueError("outcome comparison requires a predicted probability")
        return self


class InstrumentNote(_Frozen):
    id: str
    belief_id: str
    note: str
    kind: Literal["observation", "defect", "hygiene"] = "observation"
    created_at: str

    def model_post_init(self, _) -> None:
        validate_id(self.id, "IR")
