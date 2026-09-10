"""Epistemic Foundry Oracle: CEEC-compliant experiment selection.

Hard constraints are evaluated BEFORE scoring; no score can resurrect a
candidate that failed a hard constraint. Overrides are explicit, recorded in
the decision, and limited to soft preferences — never hard constraints.
"""

from __future__ import annotations

import hashlib
import json
import math
from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from computronium.ceec.gates import effective_status
from computronium.ceec.store import CEECStore, StoreError

if TYPE_CHECKING:
    from pathlib import Path

    from computronium.ceec import models

BUDGET_DEFAULT_COST = {"quick": 1.0, "standard": 4.0, "nightly": 16.0}

CoordinateValidator = Callable[[Any], None]


@dataclass(frozen=True, slots=True)
class ConstraintResult:
    constraint: str
    passed: bool
    detail: str


@dataclass(frozen=True, slots=True)
class ScoredCandidate:
    experiment_id: str
    constraints: tuple[ConstraintResult, ...]
    expected_value: float | None = None
    cost: float | None = None
    score: float | None = None

    @property
    def all_constraints_passed(self) -> bool:
        return all(c.passed for c in self.constraints)


def generate_candidates(store: CEECStore) -> list[models.Experiment]:
    """Pre-registered, not-yet-run experiments are the candidate pool."""
    return store.experiments_by_status("pre_registered")


def check_hard_constraints(
    store: CEECStore,
    experiment: models.Experiment,
    coordinate_validator: CoordinateValidator | None = None,
    budget_limit: float | None = None,
) -> tuple[ConstraintResult, ...]:
    design = experiment.design
    coordinate = design.get("coordinate")

    if coordinate is not None and coordinate_validator is not None:
        try:
            coordinate_validator(coordinate)
            coord_result = ConstraintResult("coordinate_valid", True, "validated")
        except Exception as exc:
            coord_result = ConstraintResult("coordinate_valid", False, str(exc))
    else:
        coord_result = ConstraintResult(
            "coordinate_valid", True, "not applicable (no coordinate / no validator)"
        )

    quarantined = []
    for belief_id in experiment.target_beliefs:
        eff = effective_status(store, belief_id)
        if eff.effective == "quarantined":
            quarantined.append(belief_id)

    results = [
        coord_result,
        ConstraintResult(
            "pre_registration_complete",
            experiment.status == "pre_registered",
            f"status={experiment.status}",
        ),
        ConstraintResult(
            "no_quarantined_dependencies",
            not quarantined,
            f"quarantined targets={quarantined or 'none'}",
        ),
        ConstraintResult(
            "budget_within_limit",
            budget_limit is None
            or (experiment.cost_high or BUDGET_DEFAULT_COST[experiment.budget])
            <= budget_limit,
            f"cost_high={experiment.cost_high}, budget={experiment.budget}, "
            f"limit={budget_limit}",
        ),
        ConstraintResult(
            "controls_present_or_justified",
            bool(experiment.controls) or bool(design.get("controls_justification")),
            f"controls={len(experiment.controls)}, justification="
            f"{design.get('controls_justification')}",
        ),
        ConstraintResult(
            "seed_plan_present",
            bool(design.get("seed_plan")),
            f"seed_plan={design.get('seed_plan')!r}",
        ),
        ConstraintResult(
            "evaluation_policy_present",
            bool(design.get("evaluation_policy")),
            f"evaluation_policy={design.get('evaluation_policy')!r}",
        ),
        ConstraintResult(
            "structured_evidence_plan_present",
            bool(design.get("evidence_kind")),
            f"evidence_kind={design.get('evidence_kind')!r}",
        ),
        ConstraintResult(
            "instrument_valid_for_claim",
            _instruments_valid(store, design.get("instruments", [])),
            f"instruments={design.get('instruments', [])}",
        ),
        ConstraintResult(
            "frozen_theta_audit_for_psi_only_claims",
            not design.get("psi_only") or "frozen_theta_audit" in experiment.hard_gates,
            f"psi_only={design.get('psi_only')}, "
            f"frozen_theta_audit gate={'frozen_theta_audit' in experiment.hard_gates}",
        ),
        ConstraintResult(
            "identity_card_for_new_primitive",
            not design.get("new_primitive") or bool(design.get("identity_card_ref")),
            f"new_primitive={design.get('new_primitive')}, card="
            f"{design.get('identity_card_ref')!r}",
        ),
    ]
    return tuple(results)


def _instruments_valid(store: CEECStore, instruments: list[str]) -> bool:
    for instrument in instruments:
        eff = effective_status(store, instrument)
        if eff.effective == "quarantined":
            return False
    return True


def state_hash(store: CEECStore) -> str:
    """Deterministic digest of the epistemic state relevant to selection."""
    belief_state = {
        b: (
            (r.id if (r := store.latest_revision(b)) else None),
            store.current_status(b),
        )
        for b in sorted({
            r["id"] for r in store._conn.execute("SELECT id FROM beliefs").fetchall()
        })
    }
    goal_state = {
        g: (r.id if (r := store.latest_goal_revision(g)) else None)
        for g in sorted({
            r["id"] for r in store._conn.execute("SELECT id FROM goals").fetchall()
        })
    }
    payload = {
        "beliefs": belief_state,
        "goals": goal_state,
        "quarantined": sorted(store.beliefs_by_status("quarantined")),
        "active_experiments": [e.id for e in store.experiments_by_status("running")],
        "pre_registered": [e.id for e in store.experiments_by_status("pre_registered")],
    }
    blob = json.dumps(payload, sort_keys=True)
    return hashlib.sha256(blob.encode()).hexdigest()[:16]


def expected_value(
    store: CEECStore, experiment: models.Experiment, gamma: float = 1.0
) -> tuple[float, float, float]:
    """Documented scoring model.

    EV(x) = sum over target beliefs of
        goal_priority * (1 - mid_probability) * generality_multiplier
    Cost(x) = mean(cost_low, cost_high) or budget default.
    Score(x) = EV / Cost^gamma.
    """
    ev = 0.0
    for belief_id in experiment.target_beliefs:
        revision = store.latest_revision(belief_id)
        if revision is None:
            continue
        mid = (
            revision.probability.point
            or (revision.probability.low + revision.probability.high) / 2
        )
        generality_multiplier = {
            "narrow": 1.0,
            "moderate": 1.5,
            "broad": 2.0,
            "universal": 2.5,
        }[revision.generality]
        priority = 0.0
        for goal_id in experiment.target_goals:
            goal_rev = store.latest_goal_revision(goal_id)
            if goal_rev is not None and goal_rev.scalar_utility is not None:
                priority = max(priority, goal_rev.scalar_utility)
        ev += priority * (1.0 - mid) * generality_multiplier
    cost = (
        (experiment.cost_low + experiment.cost_high) / 2
        if experiment.cost_low is not None and experiment.cost_high is not None
        else BUDGET_DEFAULT_COST[experiment.budget]
    )
    cost = max(cost, 1e-9)
    score = ev / math.pow(cost, gamma)
    return ev, cost, score


def decide(
    store: CEECStore,
    profile: dict[str, Any],
    rationale: str,
    coordinate_validator: CoordinateValidator | None = None,
    overrides: list[dict[str, Any]] | None = None,
) -> models.Decision:
    gamma = float(profile.get("cost_model", {}).get("gamma", 1.0))
    budget_limit = profile.get("budget_limit")

    candidates = generate_candidates(store)
    scored: list[ScoredCandidate] = []
    for experiment in candidates:
        constraints = check_hard_constraints(
            store, experiment, coordinate_validator, budget_limit
        )
        candidate = ScoredCandidate(experiment.id, constraints)
        if not candidate.all_constraints_passed:
            scored.append(candidate)
            continue
        ev, cost, score = expected_value(store, experiment, gamma)
        scored.append(ScoredCandidate(experiment.id, constraints, ev, cost, score))

    eligible = [c for c in scored if c.all_constraints_passed]
    selected = max(eligible, key=lambda c: c.score or 0.0, default=None)
    if overrides:
        if not all(o.get("rationale") for o in overrides):
            raise StoreError("every override requires a rationale")
        if any(o.get("bypass_hard_constraint") for o in overrides):
            raise StoreError("overrides cannot bypass hard constraints")
        selection_override = next(
            (o for o in overrides if o.get("select_experiment")), None
        )
        if selection_override is not None:
            override_id = selection_override["select_experiment"]
            if override_id not in {c.experiment_id for c in eligible}:
                raise StoreError(
                    f"override target {override_id!r} failed hard constraints"
                )
            selected = next(c for c in eligible if c.experiment_id == override_id)

    constraint_map = {
        c.experiment_id: [_asdict(r) for r in c.constraints] for c in scored
    }
    decision = store.record_decision(
        state_hash=state_hash(store),
        candidate_experiments=[c.experiment_id for c in scored],
        scores={c.experiment_id: c.score for c in eligible if c.score is not None},
        rationale=rationale,
        selected_experiment=selected.experiment_id if selected else None,
        overrides=overrides or [],
        constraints_checked=constraint_map,
    )
    return decision


def _asdict(obj: ConstraintResult) -> dict[str, Any]:
    return {
        "constraint": obj.constraint,
        "passed": obj.passed,
        "detail": obj.detail,
    }


def load_profile(path: Path) -> dict[str, Any]:
    from omegaconf import OmegaConf

    return OmegaConf.to_container(OmegaConf.load(path), resolve=True)  # type: ignore[return-value]
