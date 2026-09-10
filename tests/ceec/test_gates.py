import pytest
from conftest import link_belief

from computronium.ceec import StoreError, gates, models


def add_flagged_evidence(store, scope, quality, belief_id="B-T1"):
    artifact = store.ingest_artifact(
        b"ev-" + str(sorted(quality.items())).encode(), "result"
    )
    ev = store.record_evidence(
        "vector",
        scope,
        [artifact.id],
        axes=["seed", "metric"],
        values_ref=artifact.uri,
        quality=quality,
    )
    store._link(
        store._conn, "belief_evidence", "belief_id", belief_id, "evidence_id", [ev.id]
    )
    store._conn.commit()
    return ev


FULL_PROMOTION_QUALITY = {
    "seeds": 3,
    "matched_control": True,
    "evaluation_policy": "task/split/budget declared",
    "defect_audit": "pass",
    "reproduction": True,
}

FULL_BOUNDARY_QUALITY = {
    "seeds": 3,
    "matched_control": True,
    "defect_audit": "pass",
    "integrity_checks": "pass",
    "known_levers_exhausted": True,
}


@pytest.fixture
def promotable_belief(store, scope):
    belief_id = link_belief(store, scope, _placeholder_evidence(store, scope))
    store.update_belief(
        belief_id,
        models.Probability(
            low=0.96,
            high=0.99,
            point=0.97,
            method="heuristic_interval_based_on_gate_evidence",
        ),
        "low",
        "high",
        "narrow",
        "open",
        "strong probe results",
    )
    return belief_id


@pytest.fixture
def boundary_belief(store, scope):
    belief_id = link_belief(store, scope, _placeholder_evidence(store, scope))
    store.update_belief(
        belief_id,
        models.Probability(
            low=0.01,
            high=0.04,
            point=0.02,
            method="heuristic_interval_based_on_gate_evidence",
        ),
        "low",
        "high",
        "narrow",
        "open",
        "weak probe results",
    )
    return belief_id


def _placeholder_evidence(store, scope):
    artifact = store.ingest_artifact(b"base", "result")
    return store.record_evidence(
        "vector", scope, [artifact.id], axes=["seed"], values_ref=artifact.uri
    )


class TestPromotion:
    def test_fails_without_matched_control(self, store, scope, promotable_belief):
        add_flagged_evidence(
            store,
            scope,
            {**FULL_PROMOTION_QUALITY, "matched_control": False},
            promotable_belief,
        )
        result = gates.evaluate_promotion(store, promotable_belief)
        assert not result.all_passed
        failed = {r.gate for r in result.results if not r.passed}
        assert "matched_control" in failed

    def test_fails_with_single_seed_unless_justified(
        self, store, scope, promotable_belief
    ):
        add_flagged_evidence(
            store, scope, {**FULL_PROMOTION_QUALITY, "seeds": 1}, promotable_belief
        )
        result = gates.evaluate_promotion(store, promotable_belief)
        failed = {r.gate for r in result.results if not r.passed}
        assert "multi_seed" in failed
        add_flagged_evidence(
            store,
            scope,
            {**FULL_PROMOTION_QUALITY, "seeds": 1, "multi_seed_justified": True},
            promotable_belief,
        )
        result = gates.evaluate_promotion(store, promotable_belief)
        assert all(r.passed for r in result.results)

    def test_fails_below_probability_threshold(self, store, scope, promotable_belief):
        store.update_belief(
            promotable_belief,
            models.Probability(low=0.60, high=0.80),
            "medium",
            "medium",
            "narrow",
            "open",
            "weaker follow-up",
        )
        add_flagged_evidence(store, scope, FULL_PROMOTION_QUALITY, promotable_belief)
        result = gates.evaluate_promotion(store, promotable_belief)
        failed = {r.gate for r in result.results if not r.passed}
        assert "probability_threshold" in failed

    def test_promotion_records_gates_and_changes_status(
        self, store, scope, promotable_belief
    ):
        add_flagged_evidence(store, scope, FULL_PROMOTION_QUALITY, promotable_belief)
        result = gates.promote(store, promotable_belief, "full gate pass")
        assert result.all_passed
        assert store.current_status(promotable_belief) == "promoted"
        outcomes = store.gate_outcomes_for(belief_id=promotable_belief)
        assert len(outcomes) == 8

    def test_promotion_blocked_by_quarantined_instrument(
        self, store, scope, promotable_belief
    ):
        add_flagged_evidence(store, scope, FULL_PROMOTION_QUALITY, promotable_belief)
        dep = store.create_belief(
            "instrument claim", "instrument", scope, id_="B-INSTR", evidence_refs=[]
        )
        # make promotable_belief depend on instrument
        store._conn.execute(
            "INSERT INTO belief_dependencies VALUES (?, ?)",
            (promotable_belief, dep.id),
        )
        store._conn.commit()
        gates.quarantine(store, dep.id, "known_defect_affects_measurement", "audit gap")
        result = gates.evaluate_promotion(store, promotable_belief)
        failed = {r.gate for r in result.results if not r.passed}
        assert "no_quarantined_dependencies" in failed
        assert not result.all_passed
        assert store.current_status(promotable_belief) == "quarantined"


class TestBoundary:
    def test_fails_without_defect_hunt(self, store, scope, boundary_belief):
        add_flagged_evidence(
            store,
            scope,
            {**FULL_BOUNDARY_QUALITY, "defect_audit": "not_run"},
            boundary_belief,
        )
        result = gates.evaluate_boundary(store, boundary_belief)
        failed = {r.gate for r in result.results if not r.passed}
        assert "defect_hunt_passed" in failed

    def test_fails_with_untested_lever(self, store, scope, boundary_belief):
        add_flagged_evidence(
            store,
            scope,
            {**FULL_BOUNDARY_QUALITY, "known_levers_exhausted": False},
            boundary_belief,
        )
        result = gates.evaluate_boundary(store, boundary_belief)
        failed = {r.gate for r in result.results if not r.passed}
        assert "known_levers_exhausted" in failed

    def test_boundary_declaration_gated(self, store, scope, boundary_belief):
        add_flagged_evidence(store, scope, FULL_BOUNDARY_QUALITY, boundary_belief)
        result = gates.declare_boundary(store, boundary_belief, "levers exhausted")
        assert result.all_passed
        assert store.current_status(boundary_belief) == "boundary"


class TestReopen:
    def test_requires_recorded_trigger(self, store, scope, boundary_belief):
        with pytest.raises(StoreError, match="unknown reopen trigger"):
            gates.reopen(store, boundary_belief, "", "no trigger")

    def test_unknown_trigger_rejected(self, store, scope, boundary_belief):
        with pytest.raises(StoreError, match="unknown reopen trigger"):
            gates.reopen(store, boundary_belief, "vibes", "gut feeling")

    def test_reopen_only_from_boundary(self, store, scope, boundary_belief):
        with pytest.raises(StoreError, match="not at boundary"):
            gates.reopen(
                store, boundary_belief, "strong_untested_mechanism", "early reopen"
            )

    def test_valid_reopen(self, store, scope, boundary_belief):
        add_flagged_evidence(store, scope, FULL_BOUNDARY_QUALITY, boundary_belief)
        gates.declare_boundary(store, boundary_belief, "levers exhausted")
        change = gates.reopen(
            store,
            boundary_belief,
            "strong_untested_mechanism",
            "new mechanism found",
        )
        assert change.trigger == "strong_untested_mechanism"
        assert store.current_status(boundary_belief) == "open"


class TestStatusMachine:
    def test_status_change_without_gate_outcome_rejected(
        self, store, scope, promotable_belief
    ):
        with pytest.raises(StoreError, match="gate outcome refs"):
            store.change_status(promotable_belief, "promoted", "assertion only")

    def test_quarantined_blocks_promotion(self, store, scope, promotable_belief):
        add_flagged_evidence(store, scope, FULL_PROMOTION_QUALITY, promotable_belief)
        store.change_status(promotable_belief, "quarantined", "suspect instrument")
        with pytest.raises(StoreError, match="quarantined"):
            store.change_status(promotable_belief, "promoted", "try promotion")

    def test_effective_status_propagates_quarantine(
        self, store, scope, promotable_belief
    ):
        dep = store.create_belief(
            "instrument", "instrument", scope, id_="B-INSTR", evidence_refs=[]
        )
        store._conn.execute(
            "INSERT INTO belief_dependencies VALUES (?, ?)", (promotable_belief, dep.id)
        )
        store._conn.commit()
        eff = gates.effective_status(store, promotable_belief)
        assert eff.effective == "open"
        gates.quarantine(store, dep.id, "audit_incomplete", "missing audit")
        eff = gates.effective_status(store, promotable_belief)
        assert eff.effective == "quarantined"
        assert dep.id in eff.quarantined_by
