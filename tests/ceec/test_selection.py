import pytest
from conftest import link_belief

from computronium.ceec import StoreError, gates, models, selection


def make_experiment(
    experiment_id="X-1",
    belief_ids=(),
    goal_ids=(),
    design=None,
    controls=(),
    cost=None,
    hard_gates=("coordinate_valid",),
):
    return models.Experiment(
        id=experiment_id,
        question="does adaptive feedback improve credit?",
        rationale="tests H1",
        scope=models.Scope(domain="probe", substrate=("digital",), budget="quick"),
        target_beliefs=list(belief_ids),
        target_goals=list(goal_ids),
        design=design or {},
        prediction="improvement >= 10%",
        controls=list(controls),
        metrics=["improvement_per_norm"],
        budget="quick",
        cost_low=cost[0] if cost else None,
        cost_high=cost[1] if cost else None,
        falsification_criterion="no consistent improvement",
        overturn_criterion="rescue probability rises above 0.10",
        hard_gates=list(hard_gates),
        created_at="2026-01-01",
    )


def bootstrap_belief(store, scope, belief_id="B-H1", goal_id=None):
    artifact = store.ingest_artifact(b"ev", "result")
    ev = store.record_evidence(
        "vector", scope, [artifact.id], axes=["seed"], values_ref=artifact.uri
    )
    link_belief(store, scope, ev, belief_id)
    if goal_id:
        store.create_goal("local credit viability", "science", id_=goal_id)
        store.revise_goal(goal_id, {"science": 1.0}, scalar_utility=1.0)


PROFILE = {
    "cost_model": {"gamma": 1.0},
    "budget_limit": None,
}


class TestHardConstraints:
    def test_complete_candidate_passes(self, store, scope):
        bootstrap_belief(store, scope)
        experiment = make_experiment(
            design={
                "seed_plan": "3 seeds",
                "evaluation_policy": "quick budget, 30-step descent",
                "evidence_kind": "vector",
            },
            controls=["fixed_random_feedback"],
        )
        registered = store.pre_register_experiment(experiment)
        results = selection.check_hard_constraints(store, registered)
        assert all(r.passed for r in results)

    def test_quarantined_dependency_rejected_before_scoring(self, store, scope):
        bootstrap_belief(store, scope)
        instrument = store.create_belief(
            "instrument", "instrument", scope, id_="I-1", evidence_refs=[]
        )
        store._conn.execute(
            "INSERT INTO belief_dependencies VALUES (?, ?)", ("B-H1", instrument.id)
        )
        store._conn.commit()
        gates.quarantine(store, instrument.id, "audit_incomplete", "gap")
        experiment = make_experiment(
            experiment_id="X-1",
            belief_ids=["B-H1"],
            design={
                "seed_plan": "3",
                "evaluation_policy": "e",
                "evidence_kind": "vector",
            },
            controls=["c"],
        )
        store.pre_register_experiment(experiment)
        decision = selection.decide(store, PROFILE, "round 1")
        assert decision.selected_experiment is None
        failed = decision.constraints_checked[experiment.id]
        assert any(not r["passed"] for r in failed)

    def test_high_score_cannot_override_hard_constraint(self, store, scope):
        bootstrap_belief(store, scope, "B-H1", "G-1")
        # expensive candidate with failing constraints
        experiment = make_experiment(
            experiment_id="X-BAD",
            belief_ids=["B-H1"],
            goal_ids=["G-1"],
            design={},  # missing seed plan/evaluation policy/evidence kind
            controls=[],
        )
        store.pre_register_experiment(experiment)
        decision = selection.decide(store, PROFILE, "attempted bypass")
        assert decision.selected_experiment is None

    def test_missing_controls_rejected(self, store, scope):
        bootstrap_belief(store, scope)
        experiment = make_experiment(
            experiment_id="X-NOCTRL",
            design={
                "seed_plan": "3",
                "evaluation_policy": "e",
                "evidence_kind": "vector",
            },
            controls=[],
        )
        registered = store.pre_register_experiment(experiment)
        results = selection.check_hard_constraints(store, registered)
        failed = {r.constraint for r in results if not r.passed}
        assert "controls_present_or_justified" in failed
        # justified absence passes
        justified = make_experiment(
            experiment_id="X-JUST",
            design={
                "seed_plan": "3",
                "evaluation_policy": "e",
                "evidence_kind": "vector",
                "controls_justification": "analytic baseline",
            },
        )
        registered = store.pre_register_experiment(justified)
        results = selection.check_hard_constraints(store, registered)
        assert all(r.passed for r in results)

    def test_psi_only_requires_frozen_theta_audit_gate(self, store, scope):
        bootstrap_belief(store, scope)
        experiment = make_experiment(
            experiment_id="X-PSI",
            design={
                "seed_plan": "3",
                "evaluation_policy": "e",
                "evidence_kind": "curve",
                "psi_only": True,
            },
            controls=["c"],
        )
        registered = store.pre_register_experiment(experiment)
        results = selection.check_hard_constraints(store, registered)
        failed = {r.constraint for r in results if not r.passed}
        assert "frozen_theta_audit_for_psi_only_claims" in failed

    def test_new_primitive_requires_identity_card(self, store, scope):
        bootstrap_belief(store, scope)
        experiment = make_experiment(
            experiment_id="X-PRIM",
            design={
                "seed_plan": "3",
                "evaluation_policy": "e",
                "evidence_kind": "vector",
                "new_primitive": True,
            },
            controls=["c"],
        )
        registered = store.pre_register_experiment(experiment)
        results = selection.check_hard_constraints(store, registered)
        failed = {r.constraint for r in results if not r.passed}
        assert "identity_card_for_new_primitive" in failed


class TestDecide:
    def test_decision_recorded_with_selection(self, store, scope):
        bootstrap_belief(store, scope, "B-H1", "G-1")
        experiment = make_experiment(
            experiment_id="X-GOOD",
            belief_ids=["B-H1"],
            goal_ids=["G-1"],
            design={
                "seed_plan": "3",
                "evaluation_policy": "e",
                "evidence_kind": "vector",
            },
            controls=["c"],
        )
        store.pre_register_experiment(experiment)
        decision = selection.decide(store, PROFILE, "highest EV per cost")
        assert decision.selected_experiment == "X-GOOD"
        assert decision.state_hash
        assert decision.constraints_checked["X-GOOD"]

    def test_scoring_deterministic_under_fixed_state(self, store, scope):
        bootstrap_belief(store, scope, "B-H1", "G-1")
        experiment = make_experiment(
            experiment_id="X-DET",
            belief_ids=["B-H1"],
            goal_ids=["G-1"],
            design={
                "seed_plan": "3",
                "evaluation_policy": "e",
                "evidence_kind": "vector",
            },
            controls=["c"],
        )
        store.pre_register_experiment(experiment)
        selection.decide(store, PROFILE, "run a")
        ev1, cost1, score1 = selection.expected_value(store, experiment)
        selection.decide(store, PROFILE, "run b")
        ev2, cost2, score2 = selection.expected_value(store, experiment)
        assert (ev1, cost1, score1) == (ev2, cost2, score2)

    def test_state_hash_changes_with_state(self, store, scope):
        bootstrap_belief(store, scope)
        h1 = selection.state_hash(store)
        artifact = store.ingest_artifact(b"more", "result")
        store.record_evidence(
            "vector", scope, [artifact.id], axes=["s"], values_ref=artifact.uri
        )
        store.update_belief(
            "B-H1",
            models.Probability(low=0.4, high=0.8),
            "medium",
            "medium",
            "narrow",
            "open",
            "new evidence",
        )
        h2 = selection.state_hash(store)
        assert h1 != h2

    def test_override_without_rationale_rejected(self, store, scope):
        bootstrap_belief(store, scope)
        experiment = make_experiment(
            design={
                "seed_plan": "3",
                "evaluation_policy": "e",
                "evidence_kind": "vector",
            },
            controls=["c"],
        )
        store.pre_register_experiment(experiment)
        with pytest.raises(StoreError, match="rationale"):
            selection.decide(
                store,
                PROFILE,
                "round",
                overrides=[{"select_experiment": experiment.id}],
            )

    def test_override_cannot_target_constraint_failed_candidate(self, store, scope):
        bootstrap_belief(store, scope)
        experiment = make_experiment(
            experiment_id="X-BAD",
            design={},  # fails hard constraints
        )
        store.pre_register_experiment(experiment)
        with pytest.raises(StoreError, match="failed hard constraints"):
            selection.decide(
                store,
                PROFILE,
                "bypass attempt",
                overrides=[
                    {
                        "select_experiment": experiment.id,
                        "rationale": "manual preference",
                    }
                ],
            )

    def test_override_cannot_bypass_hard_constraints(self, store, scope):
        with pytest.raises(StoreError, match="bypass"):
            selection.decide(
                store,
                PROFILE,
                "round",
                overrides=[{"bypass_hard_constraint": True, "rationale": "urgent"}],
            )

    def test_no_candidates_yields_recorded_empty_decision(self, store):
        decision = selection.decide(store, PROFILE, "empty round")
        assert decision.selected_experiment is None
        assert decision.candidate_experiments == []
