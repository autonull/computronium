"""Integration loop (Phase H required test):

initialize ledger -> bootstrap -> select experiment -> record decision ->
pre-register -> simulate execution -> record artifact/evidence/derived ->
update belief -> evaluate gate -> record calibration -> run audit.
"""

import pytest

from computronium.ceec import (
    audit,
    bootstrap,
    calibration,
    gates,
    models,
    selection,
)
from computronium.ceec.probe_adapter import record_probe_result
from computronium.ceec.store import CEECStore


@pytest.fixture
def store(tmp_path):
    with CEECStore(tmp_path / "ceec.sqlite3", tmp_path / "artifacts") as s:
        yield s


def test_full_integration_loop(store, tmp_path):
    # 1-2. initialize + bootstrap from real configs
    result = bootstrap.bootstrap(store, "configs/ceec")
    assert len(result["experiments"]) == 5

    # 3-4. select experiment + record decision
    profile = selection.load_profile(
        __import__("pathlib").Path("configs/ceec/profile.yaml")
    )
    decision = selection.decide(store, profile, rationale="integration round 1")
    assert decision.selected_experiment is not None
    experiment = store.get_experiment(decision.selected_experiment)

    # 5. pre-registration complete (already enforced at bootstrap)

    # 6. simulate execution
    store.set_experiment_status(experiment.id, "running")
    store.set_experiment_status(experiment.id, "completed")

    # 7. record artifact/evidence/derived via probe adapter
    probe_output = {
        "status": "ok",
        "kind": "curve",
        "scope": {"domain": "credit", "substrate": ["digital"], "budget": "quick"},
        "axes": ["step"],
        "values": {"loss": [1.0, 0.95, 0.9, 0.86]},
        "quality": {
            "seeds": 3,
            "matched_control": True,
            "evaluation_policy": "quick descent quality",
            "defect_audit": "pass",
            "reproduction": True,
        },
        "defects": [],
        "summary": {"final_loss": 0.86},
    }
    probe_result = record_probe_result(store, probe_output, experiment.id)

    # 8. update belief with new evidence
    belief_id = experiment.target_beliefs[0]
    store._link(
        store._conn,
        "belief_evidence",
        "belief_id",
        belief_id,
        "evidence_id",
        [probe_result.evidence.id],
    )
    store._conn.commit()
    store.update_belief(
        belief_id,
        models.Probability(
            low=0.5,
            high=0.8,
            point=0.65,
            method="heuristic_interval_based_on_gate_evidence",
        ),
        "medium",
        "medium",
        "narrow",
        "open",
        "positive probe result",
    )

    # 9. evaluate gate (promotion attempt; below threshold -> stays open)
    evaluation = gates.evaluate_promotion(store, belief_id)
    failed = {r.gate for r in evaluation.results if not r.passed}
    assert "probability_threshold" in failed

    # 10. record calibration for the completed predicted experiment
    record = calibration.record_experiment_outcome(
        store, experiment.id, "improved", True, notes="probe success"
    )
    assert record is not None

    # 11. audit
    findings = audit.run_audit(store)
    violations = [f for f in findings if f.severity == "violation"]
    assert violations == []

    # ledger integrity end state
    assert store.current_status(belief_id) == "open"
    report = calibration.calibration_report(store)
    assert report["calibration_records"] >= 1
