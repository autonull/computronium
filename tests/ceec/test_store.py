import sqlite3

import pytest

from computronium.ceec import CEECStore, StoreError, models
from computronium.ceec.ids import validate_id


class TestArtifacts:
    def test_content_addressed_and_idempotent(self, store):
        a = store.ingest_artifact(b"payload", "result", {"run": 1})
        again = store.ingest_artifact(b"payload", "result")
        assert a.id == again.id
        assert a.sha256 == again.sha256

    def test_distinct_bytes_distinct_ids(self, store):
        a1 = store.ingest_artifact(b"one", "result")
        a2 = store.ingest_artifact(b"two", "result")
        assert a1.id != a2.id
        assert (store.artifacts_dir / a2.sha256[:2] / a2.sha256).exists()

    def test_hash_stable_across_store_instances(self, store, tmp_path):
        a = store.ingest_artifact(b"stable", "result")
        with CEECStore(store.db_path, store.artifacts_dir) as s2:
            a2 = s2.ingest_artifact(b"stable", "result")
        assert a.id == a2.id


class TestEvidence:
    def test_requires_artifact_or_justification(self, store, scope):
        with pytest.raises(StoreError, match="no_artifact_justification"):
            store.record_evidence("scalar", scope)
        ev = store.record_evidence(
            "scalar", scope, no_artifact_justification="derived analytically"
        )
        assert ev.kind == "scalar"

    def test_structured_evidence_preserved(self, store, scope):
        a = store.ingest_artifact(b"tensor-data", "result")
        ev = store.record_evidence(
            "tensor", scope, [a.id], axes=["depth", "seed"], values_ref=a.uri
        )
        assert store.get_evidence(ev.id).axes == ["depth", "seed"]

    def test_invalid_artifact_ref_rejected(self, store, scope):
        with pytest.raises(StoreError, match="missing"):
            store.record_evidence("scalar", scope, ["A-does-not-exist"])


class TestDerived:
    def test_inputs_must_exist(self, store, scope):
        with pytest.raises(StoreError, match="missing"):
            store.record_derived("summary", "mean", {"evidence": ["E-999"]}, scope)

    def test_valid_derived(self, store, scope, evidence):
        d = store.record_derived("summary", "mean", {"evidence": [evidence.id]}, scope)
        assert store.get_derived(d.id).operator == "mean"


class TestBeliefRevisions:
    def test_revision_history_preserved(self, store, scope, evidence, link_belief):
        belief_id = link_belief(evidence)
        store.update_belief(
            belief_id,
            models.Probability(low=0.3, high=0.7),
            "medium",
            "low",
            "narrow",
            "open",
            "updated after probe",
        )
        revs = store.revisions(belief_id)
        assert len(revs) == 2
        assert revs[0].probability.low == 0.2
        assert revs[1].probability.low == 0.3

    def test_revision_requires_rationale(self, store, scope, evidence, link_belief):
        link_belief(evidence)
        with pytest.raises(StoreError, match="rationale"):
            store.update_belief(
                "B-T1",
                models.Probability(low=0.3, high=0.7),
                "medium",
                "low",
                "narrow",
                "open",
                "",
            )

    def test_open_revision_requires_evidence(self, store, scope, link_belief):
        store.create_belief("no evidence", "mechanism", scope, id_="B-NE")
        with pytest.raises(StoreError, match="no evidence or derived refs"):
            store.update_belief(
                "B-NE",
                models.Probability(low=0.2, high=0.6),
                "high",
                "low",
                "narrow",
                "open",
                "bootstrap",
            )

    def test_gated_status_via_update_belief_refused(
        self, store, scope, evidence, link_belief
    ):
        link_belief(evidence)
        with pytest.raises(StoreError, match="change_status"):
            store.update_belief(
                "B-T1",
                models.Probability(low=0.96, high=0.99),
                "low",
                "high",
                "narrow",
                "promoted",
                "sneaky promotion",
            )


def _seed_all_tables(store, scope, evidence):
    artifact = store.ingest_artifact(b"seed", "result")
    store.record_evidence("scalar", scope, [artifact.id])
    derived = store.record_derived(
        "summary", "mean", {"evidence": [evidence.id]}, scope
    )
    store.create_belief(
        "dep", "mechanism", scope, id_="B-DEP", evidence_refs=[evidence.id]
    )
    store.create_belief(
        "seed",
        "mechanism",
        scope,
        id_="B-SEED",
        evidence_refs=[evidence.id],
        derived_refs=[derived.id],
        depends_on=["B-DEP"],
    )
    store.update_belief(
        "B-SEED",
        models.Probability(low=0.2, high=0.6),
        "high",
        "low",
        "narrow",
        "open",
        "seed",
    )
    goal = store.create_goal("seed goal", "science", belief_refs=["B-SEED"])
    store.revise_goal(goal.id, {"science": 1.0})
    gate = store.record_gate_outcome(
        "scope_explicit", "pass", "seed", belief_id="B-SEED"
    )
    store.record_gate_outcome("seed_plan_present", "pass", "seed", belief_id="B-SEED")
    store.change_status("B-SEED", "promoted", "seed", gate_refs=[gate.id])
    store.record_decision("hash", [], {}, "seed")
    store.record_calibration(
        "seed pred",
        predicted_probability=models.Probability(low=0.4, high=0.6, point=0.5),
    )
    store.record_instrument_note("B-DEP", "seed note")


class TestAppendOnly:
    @pytest.mark.parametrize(
        ("table", "stmt"),
        [
            ("artifacts", "UPDATE artifacts SET type = 'x'"),
            ("evidence", "DELETE FROM evidence"),
            ("evidence_artifacts", "DELETE FROM evidence_artifacts"),
            ("derived", "UPDATE derived SET operator = 'x'"),
            ("beliefs", "UPDATE beliefs SET statement = 'x'"),
            ("belief_revisions", "DELETE FROM belief_revisions"),
            ("belief_evidence", "DELETE FROM belief_evidence"),
            ("belief_derived", "DELETE FROM belief_derived"),
            ("belief_dependencies", "DELETE FROM belief_dependencies"),
            ("goals", "UPDATE goals SET statement = 'x'"),
            ("goal_revisions", "DELETE FROM goal_revisions"),
            ("goal_beliefs", "DELETE FROM goal_beliefs"),
            ("decisions", "UPDATE decisions SET rationale = 'x'"),
            ("gate_outcomes", "DELETE FROM gate_outcomes"),
            ("status_changes", "UPDATE status_changes SET to_status = 'promoted'"),
            ("calibration_records", "DELETE FROM calibration_records"),
            ("instrument_notes", "DELETE FROM instrument_notes"),
        ],
    )
    def test_triggers_block_mutation(self, store, scope, evidence, table, stmt):
        _seed_all_tables(store, scope, evidence)
        with pytest.raises(sqlite3.IntegrityError):
            store._conn.execute(stmt)

    def test_revision_chain_intact_after_status_changes(self, store, scope, evidence, link_belief):
        belief_id = link_belief(evidence)
        gate = store.record_gate_outcome(
            "probability_threshold", "pass", "ok", belief_id=belief_id
        )
        store.change_status(belief_id, "promoted", "gates", gate_refs=[gate.id])
        store.change_status(belief_id, "open", "reversal")
        revs = store.revisions(belief_id)
        assert [r.status for r in revs] == ["open", "promoted", "open"]


class TestReferentialIntegrity:
    def test_belief_missing_evidence_ref(self, store, scope):
        with pytest.raises(StoreError, match="missing"):
            store.create_belief("h", "mechanism", scope, evidence_refs=["E-404"])

    def test_status_change_unknown_gate_ref(self, store, scope, evidence, link_belief):
        belief_id = link_belief(evidence)
        with pytest.raises(StoreError, match="missing"):
            store.change_status(belief_id, "promoted", "r", gate_refs=["GO-404"])

    def test_experiment_unknown_target_belief(self, store, scope):
        with pytest.raises(StoreError, match="missing"):
            store.pre_register_experiment(
                models.Experiment(
                    id="X-1",
                    question="q",
                    rationale="r",
                    scope=scope,
                    target_beliefs=["B-404"],
                    target_goals=[],
                    design={},
                    prediction="p",
                    controls=[],
                    metrics=["m"],
                    budget="quick",
                    falsification_criterion="f",
                    overturn_criterion="o",
                    hard_gates=["coordinate_valid"],
                    created_at="2026-01-01",
                )
            )

    def test_incomplete_preregistration_rejected(self, store, scope):
        exp = models.Experiment(
            id="X-2",
            question="q",
            rationale="r",
            scope=scope,
            target_beliefs=[],
            target_goals=[],
            design={},
            prediction="",
            controls=[],
            metrics=[],
            budget="quick",
            falsification_criterion="",
            overturn_criterion="o",
            hard_gates=[],
            created_at="2026-01-01",
        )
        with pytest.raises(StoreError, match=r"incomplete|metrics and hard gates"):
            store.pre_register_experiment(exp)

    def test_double_preregistration_rejected(self, store, scope):
        exp = models.Experiment(
            id="X-3",
            question="q",
            rationale="r",
            scope=scope,
            target_beliefs=[],
            target_goals=[],
            design={},
            prediction="p",
            controls=[],
            metrics=["m"],
            budget="quick",
            falsification_criterion="f",
            overturn_criterion="o",
            hard_gates=["coordinate_valid"],
            created_at="2026-01-01",
        )
        store.pre_register_experiment(exp)
        with pytest.raises(StoreError, match="already registered"):
            store.pre_register_experiment(exp)


def test_validate_id():
    assert validate_id("B-H1", "B") == "B-H1"
    with pytest.raises(ValueError, match="expected prefix"):
        validate_id("X-1", "B")
