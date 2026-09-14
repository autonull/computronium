"""CEEC kernel profiles (TODO26 Phase A/B).

A ``Profile`` parameterizes the epistemic kernel by application domain:
thresholds, budget vocabulary, quality-flag schema, and the hard-constraint
registry. Core constraints are domain-neutral; profiles may only *add*
constraints and declare vocabulary — never weaken gate families (§17).
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from enum import StrEnum
from typing import TYPE_CHECKING, Any

from ceec.constraints import ConstraintResult

if TYPE_CHECKING:
    from ceec import models
    from ceec.store import CEECStore

ConstraintCheck = Callable[
    ["CEECStore", "models.Experiment", "Profile"], ConstraintResult
]


class LedgerRole(StrEnum):
    MAIN = "main"
    CAMPAIGN = "campaign"
    SCRATCH = "scratch"


@dataclass(frozen=True, slots=True)
class Thresholds:
    promote_low: float = 0.95
    boundary_high: float = 0.05
    reopen_min: float = 0.10


@dataclass(frozen=True, slots=True)
class QualitySchema:
    """Declared evidence quality flags; spellings live in exactly one place.

    Undeclared keys pass through (open map, spec §6); declared keys are
    validated at record time — type flags by isinstance, enum flags by
    membership in the literal tuple.
    """

    flags: Mapping[str, type | tuple[object, ...]] = field(default_factory=dict)
    required: Mapping[str, frozenset[str]] = field(default_factory=dict)

    def validate(self, quality: Mapping[str, object]) -> None:
        for key, value in quality.items():
            spec = self.flags.get(key)
            if spec is None:
                continue
            if isinstance(spec, tuple):
                if value not in spec:
                    raise ValueError(f"quality flag {key}={value!r} not in {spec}")
            elif spec is not bool and not isinstance(value, spec):
                raise ValueError(f"quality flag {key}={value!r} is not {spec.__name__}")


CORE_QUALITY_FLAGS: dict[str, type | tuple[object, ...]] = {
    "seeds": int,
    "matched_control": bool,
    "evaluation_policy": str,
    "defect_audit": ("pass", "fail", "not_run"),
    "integrity_checks": ("pass", "fail", "not_run"),
    "known_levers_exhausted": bool,
    "reproduction": bool,
    "multi_seed_justified": bool,
    "multi_seed_infeasible": bool,
}

CORE_QUALITY = QualitySchema(flags=CORE_QUALITY_FLAGS)


@dataclass(frozen=True, slots=True)
class Constraint:
    name: str
    check: ConstraintCheck


@dataclass(frozen=True, slots=True)
class Profile:
    name: str
    policy_version: str = "1.0"
    scope_dimensions: Mapping[str, type] = field(default_factory=dict)
    budget_tiers: tuple[str, ...] = ("quick", "standard", "nightly")
    tier_budget: Mapping[str, str] | None = None
    default_cost: Mapping[str, float] | None = None
    budget_limit: float | None = None
    gamma: float = 1.0
    constraints: tuple[Constraint, ...] = ()
    quality: QualitySchema = field(default_factory=QualitySchema)
    thresholds: Thresholds = field(default_factory=Thresholds)


def coordinate_constraint(validator: Callable[[Any], None]) -> Constraint:
    """Factory: bind a domain coordinate validator as a named constraint."""

    def check(
        store: CEECStore, experiment: models.Experiment, _profile: Profile
    ) -> ConstraintResult:
        coordinate = experiment.design.get("coordinate")
        if coordinate is None:
            return ConstraintResult(
                "coordinate_valid", True, "not applicable (no coordinate)"
            )
        try:
            validator(coordinate)
        except Exception as exc:
            return ConstraintResult("coordinate_valid", False, str(exc))
        return ConstraintResult("coordinate_valid", True, "validated")

    return Constraint("coordinate_valid", check)


def _pre_registration_complete(
    store: CEECStore, experiment: models.Experiment, _profile: Profile
) -> ConstraintResult:
    return ConstraintResult(
        "pre_registration_complete",
        experiment.status == "pre_registered",
        f"status={experiment.status}",
    )


def _no_quarantined_dependencies(
    store: CEECStore, experiment: models.Experiment, _profile: Profile
) -> ConstraintResult:
    from ceec.gates import effective_status

    quarantined = [
        belief_id
        for belief_id in experiment.target_beliefs
        if effective_status(store, belief_id).effective == "quarantined"
    ]
    return ConstraintResult(
        "no_quarantined_dependencies",
        not quarantined,
        f"quarantined targets={quarantined or 'none'}",
    )


def _budget_within_limit(
    store: CEECStore, experiment: models.Experiment, profile: Profile
) -> ConstraintResult:
    cost = experiment.cost_high or (profile.default_cost or {}).get(
        experiment.budget, 1.0
    )
    return ConstraintResult(
        "budget_within_limit",
        profile.budget_limit is None or cost <= profile.budget_limit,
        f"cost_high={experiment.cost_high}, budget={experiment.budget}, "
        f"limit={profile.budget_limit}",
    )


def _controls_present_or_justified(
    store: CEECStore, experiment: models.Experiment, _profile: Profile
) -> ConstraintResult:
    design = experiment.design
    return ConstraintResult(
        "controls_present_or_justified",
        bool(experiment.controls) or bool(design.get("controls_justification")),
        f"controls={len(experiment.controls)}, justification="
        f"{design.get('controls_justification')}",
    )


def _seed_plan_present(
    store: CEECStore, experiment: models.Experiment, _profile: Profile
) -> ConstraintResult:
    return ConstraintResult(
        "seed_plan_present",
        bool(experiment.design.get("seed_plan")),
        f"seed_plan={experiment.design.get('seed_plan')!r}",
    )


def _evaluation_policy_present(
    store: CEECStore, experiment: models.Experiment, _profile: Profile
) -> ConstraintResult:
    design = experiment.design
    return ConstraintResult(
        "evaluation_policy_present",
        bool(design.get("evaluation_policy")),
        f"evaluation_policy={design.get('evaluation_policy')!r}",
    )


def _structured_evidence_plan_present(
    store: CEECStore, experiment: models.Experiment, _profile: Profile
) -> ConstraintResult:
    design = experiment.design
    return ConstraintResult(
        "structured_evidence_plan_present",
        bool(design.get("evidence_kind")),
        f"evidence_kind={design.get('evidence_kind')!r}",
    )


def _instrument_valid_for_claim(
    store: CEECStore, experiment: models.Experiment, _profile: Profile
) -> ConstraintResult:
    from ceec.gates import effective_status

    instruments = experiment.design.get("instruments", [])
    valid = all(
        effective_status(store, instrument).effective != "quarantined"
        for instrument in instruments
    )
    return ConstraintResult(
        "instrument_valid_for_claim", valid, f"instruments={instruments}"
    )


CORE_CONSTRAINTS: tuple[Constraint, ...] = (
    Constraint("pre_registration_complete", _pre_registration_complete),
    Constraint("no_quarantined_dependencies", _no_quarantined_dependencies),
    Constraint("budget_within_limit", _budget_within_limit),
    Constraint("controls_present_or_justified", _controls_present_or_justified),
    Constraint("seed_plan_present", _seed_plan_present),
    Constraint("evaluation_policy_present", _evaluation_policy_present),
    Constraint("structured_evidence_plan_present", _structured_evidence_plan_present),
    Constraint("instrument_valid_for_claim", _instrument_valid_for_claim),
)

DEFAULT_PROFILE = Profile(
    name="ceec-core",
    constraints=CORE_CONSTRAINTS,
    default_cost={"quick": 1.0, "standard": 4.0, "nightly": 16.0},
    quality=CORE_QUALITY,
)
