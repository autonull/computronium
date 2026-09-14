"""Epistemic Foundry Oracle: CEEC-compliant experiment selection.

Hard constraints are evaluated BEFORE scoring; no score can resurrect a
candidate that failed a hard constraint. Overrides are explicit, recorded in
the decision, and limited to soft preferences — never hard constraints.
"""

from __future__ import annotations

import hashlib
import json
import math
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from ceec.profile import DEFAULT_PROFILE, Profile
from ceec.store import CEECStore, StoreError

if TYPE_CHECKING:
    from pathlib import Path

    from ceec import models
    from ceec.constraints import ConstraintResult

CoordinateValidator = Callable[[Any], None]


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
    profile: Profile | None = None,
) -> tuple[ConstraintResult, ...]:
    """Run the profile's constraint registry in order."""
    from ceec.profile import coordinate_constraint

    profile = profile or DEFAULT_PROFILE
    coord = (
        coordinate_constraint(coordinate_validator) if coordinate_validator else None
    )
    return tuple(
        constraint.check(store, experiment, profile)
        for constraint in ((coord,) if coord else ()) + profile.constraints
    )


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
    store: CEECStore, experiment: models.Experiment, profile: Profile | None = None
) -> tuple[float, float, float]:
    """Documented scoring model.

    EV(x) = sum over target beliefs of
        goal_priority * (1 - mid_probability) * generality_multiplier
    Cost(x) = mean(cost_low, cost_high) or budget default.
    Score(x) = EV / Cost^gamma.
    """
    profile = profile or store.profile or DEFAULT_PROFILE
    gamma = profile.gamma
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
    default_cost = profile.default_cost or {}
    cost = (
        (experiment.cost_low + experiment.cost_high) / 2
        if experiment.cost_low is not None and experiment.cost_high is not None
        else default_cost.get(experiment.budget, 1.0)
    )
    cost = max(cost, 1e-9)
    score = ev / math.pow(cost, gamma)
    return ev, cost, score


def decide(  # noqa: PLR0914 -- §22 loop accumulates scored candidates
    store: CEECStore,
    profile: Profile | None,
    rationale: str,
    coordinate_validator: CoordinateValidator | None = None,
    overrides: list[dict[str, Any]] | None = None,
    candidate_ids: Sequence[str] | None = None,
) -> models.Decision:
    """§22 selection loop.

    ``candidate_ids`` (TODO25 T25.A.3) restricts the pool to a pre-registered
    subset — e.g. one evolution generation's experiments — without
    widening the loop's logic. ``None`` keeps the store-wide default.

    A ``select_experiment`` override on a single-eligible-candidate pool
    is vacuous (no alternative to select against): it is validated but
    not recorded, so §24 ``override_rate`` keeps signal for real
    overrides.
    """
    profile = profile or store.profile or DEFAULT_PROFILE

    candidates = generate_candidates(store)
    if candidate_ids is not None:
        wanted = set(candidate_ids)
        candidates = [e for e in candidates if e.id in wanted]
    scored: list[ScoredCandidate] = []
    for experiment in candidates:
        constraints = check_hard_constraints(
            store, experiment, coordinate_validator, profile
        )
        candidate = ScoredCandidate(experiment.id, constraints)
        if not candidate.all_constraints_passed:
            scored.append(candidate)
            continue
        ev, cost, score = expected_value(store, experiment, profile)
        scored.append(ScoredCandidate(experiment.id, constraints, ev, cost, score))

    eligible = [c for c in scored if c.all_constraints_passed]
    selected = max(eligible, key=lambda c: c.score or 0.0, default=None)
    recorded_overrides = list(overrides or [])
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
            if len(eligible) <= 1:
                recorded_overrides = [
                    o for o in recorded_overrides if o is not selection_override
                ]

    decision = store.record_decision(
        state_hash=state_hash(store),
        candidate_experiments=[c.experiment_id for c in scored],
        scores={c.experiment_id: c.score for c in eligible if c.score is not None},
        rationale=rationale,
        selected_experiment=selected.experiment_id if selected else None,
        overrides=recorded_overrides,
        constraints_checked={
            c.experiment_id: [
                {"constraint": r.name, "passed": r.passed, "detail": r.detail}
                for r in c.constraints
            ]
            for c in scored
        },
        policy_version=profile.policy_version,
    )
    return decision


def load_profile(path: Path) -> Profile:
    """Load a YAML profile file into a :class:`Profile` (thresholds, gamma,
    budget_limit); constraint membership is code-registered, never YAML."""
    from omegaconf import OmegaConf

    from ceec.profile import Thresholds

    raw: dict[str, Any] = OmegaConf.to_container(OmegaConf.load(path), resolve=True)  # type: ignore[assignment]
    thresholds_raw = raw.get("thresholds") or {}
    cost_model = raw.get("cost_model") or {}
    return Profile(
        name=str(raw.get("name", "yaml-profile")),
        policy_version=str(raw.get("policy_version", "1.0")),
        thresholds=Thresholds(
            promote_low=float(thresholds_raw.get("promote", 0.95)),
            boundary_high=float(thresholds_raw.get("boundary", 0.05)),
            reopen_min=float(thresholds_raw.get("reopen", 0.10)),
        ),
        gamma=float(cost_model.get("gamma", 1.0)),
        constraints=DEFAULT_PROFILE.constraints,
        default_cost=DEFAULT_PROFILE.default_cost,
    )
