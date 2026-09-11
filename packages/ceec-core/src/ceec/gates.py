"""CEEC gate engine, status machine, and quarantine propagation.

Gate evaluation reads evidence `quality` metadata recorded by probes:

    seeds: int                      -> multi_seed
    matched_control: bool           -> matched_control
    evaluation_policy: str          -> evaluation_policy_valid
    defect_audit: "pass" | "fail"   -> defect_audit / defect_hunt_passed
    integrity_checks: "pass"        -> integrity_checks_passed
    known_levers_exhausted: bool    -> known_levers_exhausted
    reproduction: bool | >=2 artifacts -> reproduction

No status transition to promoted/boundary can occur without recorded gate
outcomes; `change_status` in the store enforces this at the ledger level.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from ceec.store import CEECStore, StoreError

if TYPE_CHECKING:
    from ceec import models

PROMOTE_THRESHOLD = 0.95
BOUNDARY_THRESHOLD = 0.05
REOPEN_THRESHOLD = 0.10

MIN_SEEDS = 3


@dataclass(frozen=True, slots=True)
class GateResult:
    gate: str
    passed: bool
    rationale: str


@dataclass(frozen=True, slots=True)
class Evaluation:
    kind: str  # "promotion" | "boundary"
    all_passed: bool
    results: tuple[GateResult, ...]
    gate_outcome_ids: tuple[str, ...] = field(default_factory=tuple)


def _evidence_for(store: CEECStore, belief_id: str) -> list[models.Evidence]:
    rows = store._conn.execute(
        "SELECT evidence_id FROM belief_evidence WHERE belief_id = ?", (belief_id,)
    ).fetchall()
    return [store.get_evidence(r["evidence_id"]) for r in rows]


def _derived_for(store: CEECStore, belief_id: str) -> list[models.Derived]:
    rows = store._conn.execute(
        "SELECT derived_id FROM belief_derived WHERE belief_id = ?", (belief_id,)
    ).fetchall()
    return [store.get_derived(r["derived_id"]) for r in rows]


def _quality_flags(evidence: list[models.Evidence]) -> dict[str, object]:
    merged: dict[str, object] = {}
    for ev in evidence:
        merged.update(ev.quality)
    return merged


def _scope_explicit(belief: models.Belief) -> bool:
    scope = belief.scope
    return bool(scope.domain) and bool(
        scope.substrate or scope.geometry or scope.credit or scope.extra
    )


def _record(
    store: CEECStore,
    belief_id: str,
    results: list[GateResult],
    evidence: list[models.Evidence],
    derived: list[models.Derived],
) -> tuple[str, ...]:
    ids = []
    for res in results:
        outcome = store.record_gate_outcome(
            gate=res.gate,
            status="pass" if res.passed else "fail",
            rationale=res.rationale,
            evidence_refs=[e.id for e in evidence],
            derived_refs=[d.id for d in derived],
            belief_id=belief_id,
        )
        ids.append(outcome.id)
    return tuple(ids)


def evaluate_promotion(store: CEECStore, belief_id: str) -> Evaluation:
    belief = store.get_belief(belief_id)
    revision = store.latest_revision(belief_id)
    evidence = _evidence_for(store, belief_id)
    derived = _derived_for(store, belief_id)
    flags = _quality_flags(evidence)

    prob_ok = revision is not None and revision.probability.low >= PROMOTE_THRESHOLD
    seeds = max([int(ev.quality.get("seeds", 0)) for ev in evidence] + [0])
    quarantined_deps = _quarantined_deps(store, belief_id)
    self_quarantined = store.current_status(belief_id) == "quarantined"
    results = [
        GateResult(
            "probability_threshold",
            prob_ok,
            f"probability_low={revision.probability.low if revision else None} "
            f"vs threshold {PROMOTE_THRESHOLD}",
        ),
        GateResult(
            "multi_seed",
            seeds >= MIN_SEEDS or flags.get("multi_seed_justified") is True,
            f"seeds={seeds} (min {MIN_SEEDS}, justified={flags.get('multi_seed_justified')})",
        ),
        GateResult(
            "matched_control",
            flags.get("matched_control") is True,
            f"matched_control={flags.get('matched_control')}",
        ),
        GateResult(
            "evaluation_policy_valid",
            bool(flags.get("evaluation_policy")),
            f"evaluation_policy={flags.get('evaluation_policy')!r}",
        ),
        GateResult(
            "defect_audit",
            flags.get("defect_audit") == "pass"
            and not any(ev.defects for ev in evidence),
            f"defect_audit={flags.get('defect_audit')}, open defects="
            f"{[ev.defects for ev in evidence if ev.defects]}",
        ),
        GateResult(
            "reproduction",
            flags.get("reproduction") is True
            or len({ev.values_ref for ev in evidence}) >= 2,
            f"reproduction flag={flags.get('reproduction')}, distinct value refs="
            f"{len({ev.values_ref for ev in evidence})}",
        ),
        GateResult(
            "scope_explicit",
            _scope_explicit(belief),
            f"scope domain={belief.scope.domain!r}",
        ),
        GateResult(
            "no_quarantined_dependencies",
            not quarantined_deps and not self_quarantined,
            f"quarantined dependencies={quarantined_deps}, "
            f"belief quarantined={self_quarantined}",
        ),
    ]
    outcome_ids = _record(store, belief_id, results, evidence, derived)
    return Evaluation(
        "promotion",
        all(r.passed for r in results),
        tuple(results),
        outcome_ids,
    )


def evaluate_boundary(store: CEECStore, belief_id: str) -> Evaluation:
    belief = store.get_belief(belief_id)
    revision = store.latest_revision(belief_id)
    evidence = _evidence_for(store, belief_id)
    derived = _derived_for(store, belief_id)
    flags = _quality_flags(evidence)

    rescue_ok = revision is not None and revision.probability.high <= BOUNDARY_THRESHOLD
    seeds = max([int(ev.quality.get("seeds", 0)) for ev in evidence] + [0])
    results = [
        GateResult(
            "rescue_probability_threshold",
            rescue_ok,
            f"rescue probability_high={revision.probability.high if revision else None} "
            f"vs threshold {BOUNDARY_THRESHOLD}",
        ),
        GateResult(
            "defect_hunt_passed",
            flags.get("defect_audit") == "pass",
            f"defect_audit={flags.get('defect_audit')}",
        ),
        GateResult(
            "integrity_checks_passed",
            flags.get("integrity_checks") == "pass",
            f"integrity_checks={flags.get('integrity_checks')}",
        ),
        GateResult(
            "known_levers_exhausted",
            flags.get("known_levers_exhausted") is True,
            f"known_levers_exhausted={flags.get('known_levers_exhausted')}",
        ),
        GateResult(
            "matched_control",
            flags.get("matched_control") is True,
            f"matched_control={flags.get('matched_control')}",
        ),
        GateResult(
            "multi_seed_where_feasible",
            seeds >= MIN_SEEDS or flags.get("multi_seed_infeasible") is True,
            f"seeds={seeds}, infeasible justification={flags.get('multi_seed_infeasible')}",
        ),
        GateResult(
            "scope_explicit",
            _scope_explicit(belief),
            f"scope domain={belief.scope.domain!r}",
        ),
    ]
    outcome_ids = _record(store, belief_id, results, evidence, derived)
    return Evaluation(
        "boundary", all(r.passed for r in results), tuple(results), outcome_ids
    )


def promote(store: CEECStore, belief_id: str, reason: str) -> Evaluation:
    evaluation = evaluate_promotion(store, belief_id)
    if evaluation.all_passed and store.current_status(belief_id) != "promoted":
        store.change_status(
            belief_id,
            "promoted",
            reason,
            gate_refs=list(evaluation.gate_outcome_ids),
        )
    return evaluation


def declare_boundary(store: CEECStore, belief_id: str, reason: str) -> Evaluation:
    evaluation = evaluate_boundary(store, belief_id)
    if evaluation.all_passed and store.current_status(belief_id) != "boundary":
        store.change_status(
            belief_id,
            "boundary",
            reason,
            gate_refs=list(evaluation.gate_outcome_ids),
        )
    return evaluation


REOPEN_TRIGGERS: frozenset[str] = frozenset({
    "strong_untested_mechanism",
    "new_evidence_raises_rescue_probability",
    "instrument_defect_invalidates_boundary",
    "decisive_omitted_control_discovered",
})


def reopen(
    store: CEECStore,
    belief_id: str,
    trigger: str,
    reason: str,
    evidence_refs: list[str] | None = None,
) -> models.StatusChange:
    if trigger not in REOPEN_TRIGGERS:
        raise StoreError(f"unknown reopen trigger {trigger!r}")
    if store.current_status(belief_id) != "boundary":
        raise StoreError(f"belief {belief_id} is not at boundary; reopen refused")
    revision = store.latest_revision(belief_id)
    if revision is not None and revision.probability.high <= REOPEN_THRESHOLD:
        pass  # trigger itself is the credible basis; probability updated by caller
    return store.change_status(
        belief_id,
        "open",
        reason,
        trigger=trigger,
        evidence_refs=evidence_refs,
    )


def quarantine(
    store: CEECStore,
    belief_id: str,
    trigger: str,
    reason: str,
    evidence_refs: list[str] | None = None,
) -> list[models.StatusChange]:
    if trigger not in _QUARANTINE_TRIGGERS:
        raise StoreError(f"unknown quarantine trigger {trigger!r}")
    changes = []
    for target in [belief_id, *_transitive_dependents(store, belief_id)]:
        status = store.current_status(target)
        if status == "quarantined":
            continue
        note = (
            reason
            if target == belief_id
            else f"propagated quarantine from {belief_id}: {reason}"
        )
        changes.append(
            store.change_status(
                target,
                "quarantined",
                note,
                trigger=trigger,
                evidence_refs=evidence_refs,
            )
        )
    return changes


def unquarantine(
    store: CEECStore,
    belief_id: str,
    reason: str,
    evidence_refs: list[str] | None = None,
) -> list[models.StatusChange]:
    if store.current_status(belief_id) != "quarantined":
        raise StoreError(f"belief {belief_id} is not quarantined")
    changes = []
    for target in [belief_id, *_transitive_dependents(store, belief_id)]:
        if store.current_status(target) != "quarantined":
            continue
        note = (
            reason
            if target == belief_id
            else f"propagated unquarantine from {belief_id}: {reason}"
        )
        changes.append(
            store.change_status(target, "open", note, evidence_refs=evidence_refs)
        )
    return changes


@dataclass(frozen=True, slots=True)
class EffectiveStatus:
    belief_id: str
    primary: str
    quarantined_by: tuple[str, ...]
    stale_by: tuple[str, ...]

    @property
    def effective(self) -> str:
        if self.primary == "quarantined" or self.quarantined_by:
            return "quarantined"
        return self.primary


def effective_status(store: CEECStore, belief_id: str) -> EffectiveStatus:
    primary = store.current_status(belief_id)
    quarantined_by = _quarantined_deps(store, belief_id)
    stale_by = _stale_deps(store, belief_id)
    return EffectiveStatus(
        belief_id=belief_id,
        primary=primary,
        quarantined_by=quarantined_by,
        stale_by=stale_by,
    )


_QUARANTINE_TRIGGERS: frozenset[str] = frozenset({
    "known_defect_affects_measurement",
    "estimator_mislabeled",
    "audit_incomplete",
    "config_provenance_mismatch",
    "dependent_artifact_stale",
    "correction_invalidates_measurement",
    "live_patch_unverified",
})


def _transitive_dependents(store: CEECStore, belief_id: str) -> list[str]:
    seen: list[str] = []
    frontier = [belief_id]
    while frontier:
        current = frontier.pop()
        for dep in store.dependents_of(current):
            if dep not in seen and dep != belief_id:
                seen.append(dep)
                frontier.append(dep)
    return seen


def _quarantined_deps(store: CEECStore, belief_id: str) -> tuple[str, ...]:
    quarantined = set(store.beliefs_by_status("quarantined"))
    deps = set(store.belief_dependencies(belief_id)) & quarantined
    return tuple(sorted(deps))


def _no_quarantined_deps(store: CEECStore, belief_id: str) -> bool:
    return not _quarantined_deps(store, belief_id)


def _stale_deps(store: CEECStore, belief_id: str) -> tuple[str, ...]:
    own = store.latest_revision(belief_id)
    if own is None:
        return ()
    stale = []
    for dep in store.belief_dependencies(belief_id):
        if _dep_content_changed_since(store, dep, own.created_at):
            stale.append(dep)
    return tuple(sorted(stale))


def _dep_content_changed_since(store: CEECStore, dep_id: str, since: str) -> bool:
    rows = store._conn.execute(
        "SELECT probability_low, probability_high, evidence_weight, created_at "
        "FROM belief_revisions WHERE belief_id = ? ORDER BY created_at",
        (dep_id,),
    ).fetchall()
    prior = [r for r in rows if r["created_at"] <= since]
    newer = [r for r in rows if r["created_at"] > since]
    if not newer:
        return False
    if not prior:
        return True
    base = prior[-1]
    latest = newer[-1]
    return (
        base["probability_low"],
        base["probability_high"],
        base["evidence_weight"],
    ) != (
        latest["probability_low"],
        latest["probability_high"],
        latest["evidence_weight"],
    )
