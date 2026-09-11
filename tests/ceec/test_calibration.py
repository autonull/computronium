import pytest

from computronium.ceec import calibration, models


@pytest.fixture
def predicted_experiment(store, scope, link_belief):
    belief_id = link_belief(_evidence(store, scope), "B-H1")
    store.create_goal("credit viability", "science", id_="G-1", belief_refs=[belief_id])
    store.revise_goal("G-1", {"science": 1.0}, scalar_utility=1.0)
    experiment = models.Experiment(
        id="X-PRED",
        question="does it work?",
        rationale="test",
        scope=scope,
        target_beliefs=[belief_id],
        target_goals=["G-1"],
        design={"seed_plan": "3", "evaluation_policy": "e", "evidence_kind": "vector"},
        prediction="improvement",
        prediction_probability=models.Probability(
            low=0.3, high=0.7, point=0.5, method="mid"
        ),
        controls=["c"],
        metrics=["m"],
        budget="quick",
        falsification_criterion="no improvement",
        overturn_criterion="rescue > 0.10",
        hard_gates=["coordinate_valid"],
        created_at="2026-01-01",
    )
    store.pre_register_experiment(experiment)
    return belief_id


def _evidence(store, scope):
    artifact = store.ingest_artifact(b"ev", "result")
    return store.record_evidence(
        "vector", scope, [artifact.id], axes=["seed"], values_ref=artifact.uri
    )


class TestCalibration:
    def test_outcome_recorded_with_scores(self, store, predicted_experiment):
        store.set_experiment_status("X-PRED", "completed")
        record = calibration.record_experiment_outcome(
            store, "X-PRED", "improved", True
        )
        assert record is not None
        assert record.brier_score == pytest.approx(0.25)
        assert record.log_score == pytest.approx(-0.6931, abs=1e-3)

    def test_no_probability_no_record(self, store, predicted_experiment):
        experiment = store.get_experiment("X-PRED")
        bare = experiment.model_copy(
            update={
                "prediction_probability": None,
                "id": "X-BARE",
                "status": "draft",
            }
        )
        store.pre_register_experiment(bare)
        store.set_experiment_status("X-BARE", "completed")
        assert (
            calibration.record_experiment_outcome(store, "X-BARE", "done", True) is None
        )

    def test_report_rates(self, store, predicted_experiment):
        gate = store.record_gate_outcome(
            "probability_threshold", "pass", "ok", belief_id=predicted_experiment
        )
        store.change_status(
            predicted_experiment, "promoted", "strong", gate_refs=[gate.id]
        )
        store.change_status(predicted_experiment, "open", "reversal")
        store.set_experiment_status("X-PRED", "completed")
        calibration.record_experiment_outcome(store, "X-PRED", "improved", True)
        report = calibration.calibration_report(store)
        assert report["calibration_records"] == 1
        assert report["promotions"] == 1
        assert report["promotion_reversal_rate"] == 1.0
        assert report["observed_success_rate"] == 1.0

    def test_review_flags(self, store, predicted_experiment):
        gate = store.record_gate_outcome(
            "probability_threshold", "pass", "ok", belief_id=predicted_experiment
        )
        store.change_status(
            predicted_experiment, "promoted", "strong", gate_refs=[gate.id]
        )
        store.change_status(predicted_experiment, "open", "reversal")
        report = calibration.calibration_report(store)
        flags = calibration.review_flags(report)
        assert "promotion_reversal_rate_high" in flags
