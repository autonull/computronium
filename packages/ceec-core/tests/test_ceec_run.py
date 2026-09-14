"""TODO25 C.2/C.4/C.5: closed-loop `ceec.run.run_experiment`, decision
quality audit, and the §24 drift review cadence — a fresh ledger built
end-to-end through `run_experiment` passes `run_audit` with zero
hand-assembled payloads."""

from __future__ import annotations

import pytest
from ceec.audit import audit_decisions, run_audit
from ceec.calibration import belief_drift, calibration_report, review_belief
from ceec.gates import declare_boundary
from ceec.run import ProbeResult, run_experiment
from ceec.selection import decide
from ceec.store import CEECStore, StoreError

from ceec import builders, models

SCOPE = models.Scope(domain="test", substrate=("digital",), budget="quick")


@pytest.fixture()
def store(tmp_path):
    s = CEECStore(tmp_path / "ledger.sqlite3", tmp_path / "artifacts")
    yield s
    s.close()


def _probe(result: ProbeResult):
    return lambda _experiment: result


def _good_result() -> ProbeResult:
    return ProbeResult(
        label="at_chance",
        outcome_boolean=True,
        payload={"mean": 0.513, "n_seeds": 3},
        axes=("seed",),
        values=(0.469, 0.539, 0.531),
        values_ref="probe/accuracies",
        quality={
            "seeds": 3,
            "matched_control": True,
            "evaluation_policy": "certified_operating_point",
        },
        notes="closed-loop probe",
    )


def test_closed_loop_records_decision_evidence_and_calibration(
    store: CEECStore,
) -> None:
    draft = builders.experiment(
        id_="X-LOOP-001",
        question="is the mean at chance?",
        prediction="mean within the 2-SE chance band",
        scope=SCOPE,
        tier="certified",
        prediction_probability=(0.3, 0.7, 0.5),
    )
    run = run_experiment(store, draft, _probe(_good_result()))
    assert run.status == "completed"
    assert store.get_experiment("X-LOOP-001").status == "completed"
    assert run.decision_id.startswith("DEC-")
    assert run.calibration_id is not None
    findings, summary = audit_decisions(store)
    assert findings == []
    assert summary["decisions"] == 1
    assert run_audit(store) == []


def test_boundary_evaluation_gates_the_status_change(store: CEECStore) -> None:
    evidence = builders.gate_evidence(
        store,
        SCOPE,
        axes=["seed"],
        values=[0.469, 0.539, 0.531],
        values_ref="probe/accuracies",
        seeds=3,
        matched_control=True,
        evaluation_policy="certified_operating_point",
        defect_audit="pass",
        integrity_checks="pass",
        known_levers_exhausted=True,
        notes="chance-band evidence",
    )
    belief = store.create_belief(
        "mechanism at chance", "mechanism", SCOPE, evidence_refs=[evidence.id]
    )
    store.update_belief(
        belief.id,
        models.Probability(low=0.0, high=0.05, method="certified_chance_boundary"),
        "low",
        "high",
        "narrow",
        "open",
        "rescue probability capped at the boundary threshold",
    )
    draft = builders.experiment(
        id_="X-LOOP-002",
        question="does the boundary hold?",
        prediction="no lever breaks chance",
        scope=SCOPE,
        tier="certified",
        target_beliefs=[belief.id],
    )
    run = run_experiment(store, draft, _probe(_good_result()), evaluate="boundary")
    assert run.evaluation is not None and run.evaluation.all_passed
    assert store.current_status(belief.id) == "boundary"


def test_failed_probe_records_failed_outcome_not_exception(store: CEECStore) -> None:
    draft = builders.experiment(
        id_="X-LOOP-003",
        question="does the probe survive?",
        prediction="it does",
        scope=SCOPE,
    )

    def _boom(_experiment: models.Experiment) -> ProbeResult:
        raise RuntimeError("probe exploded")

    run = run_experiment(store, draft, _boom)
    assert run.status == "failed"
    assert store.get_experiment("X-LOOP-003").status == "failed"
    assert run.error is not None and "probe exploded" in run.error
    assert run_audit(store) == []


def test_run_refuses_unmeasurable_and_non_draft(store: CEECStore) -> None:
    draft = builders.experiment(
        id_="X-LOOP-004",
        question="q",
        prediction="p",
        scope=SCOPE,
        controls=(),  # fails controls_present_or_justified
        design={"controls_justification": None},
    )
    with pytest.raises(Exception, match="hard constraints"):
        store.pre_register_experiment(draft)
        run_experiment(store, "X-LOOP-004", _probe(_good_result()))
    with pytest.raises(StoreError, match="not found"):
        run_experiment(store, "X-MISSING-9", _probe(_good_result()))


def test_vacuous_single_candidate_override_unrecorded(store: CEECStore) -> None:
    draft = builders.experiment(
        id_="X-SCOPE-1",
        question="q",
        prediction="p",
        scope=SCOPE,
    )
    store.pre_register_experiment(draft)
    decision = decide(
        store,
        {},
        "single-candidate pool",
        candidate_ids=["X-SCOPE-1"],
        overrides=[{"rationale": "only candidate", "select_experiment": "X-SCOPE-1"}],
    )
    assert decision.selected_experiment == "X-SCOPE-1"
    assert decision.overrides == []
    with pytest.raises(StoreError, match="failed hard constraints"):
        decide(
            store,
            {},
            "ineligible override target still raises",
            candidate_ids=["X-SCOPE-1"],
            overrides=[{"rationale": "r", "select_experiment": "X-MISSING-9"}],
        )


def test_closed_loop_override_rate_stays_clean(store: CEECStore) -> None:
    draft = builders.experiment(
        id_="X-LOOP-005",
        question="does the single-candidate decision stay a non-override?",
        prediction="override_rate remains 0.0",
        scope=SCOPE,
    )
    run = run_experiment(store, draft, _probe(_good_result()))
    assert run.status == "completed"
    assert calibration_report(store)["override_rate"] == 0.0


def test_drift_cadence_flags_and_reviews(store: CEECStore) -> None:
    artifact = store.ingest_artifact(b"drift-review", "test_payload", {})
    evidence = builders.gate_evidence(
        store,
        SCOPE,
        artifact_refs=[artifact.id],
        axes=("review",),
        values_ref="drift/review",
        seeds=3,
        matched_control=True,
        evaluation_policy="drift_review_v1",
        known_levers_exhausted=True,
    )
    belief = store.create_belief(
        "calibrated belief", "instrument", SCOPE, evidence_refs=[evidence.id]
    )
    store.update_belief(
        belief.id,
        models.Probability(low=0.0, high=0.05, method="boundary"),
        "low",
        "high",
        "narrow",
        "open",
        "boundary prior",
    )
    declare_boundary(store, belief.id, "test boundary")
    store.record_calibration(
        prediction="r1",
        belief_id=belief.id,
        predicted_probability=models.Probability(low=0.4, high=0.6, point=0.5),
        outcome_boolean=True,
    )
    store.record_calibration(
        prediction="r2",
        belief_id=belief.id,
        predicted_probability=models.Probability(low=0.1, high=0.3, point=0.2),
        outcome_boolean=True,
    )
    drift = belief_drift(store)
    assert drift[belief.id]["flagged"] is True
    assert drift[belief.id]["drift"] > 0.15

    note = review_belief(
        store, belief.id, action="acknowledge", reason="watched, benign"
    )
    assert isinstance(note, models.InstrumentNote) and note.kind == "hygiene"
    change = review_belief(
        store,
        belief.id,
        action="reopen",
        reason="drift invalidates the boundary",
        trigger="new_evidence_raises_rescue_probability",
        evidence_refs=[evidence.id],
    )
    assert isinstance(change, models.StatusChange)
    assert change.from_status == "boundary"
    assert change.to_status == "open"
    with pytest.raises(ValueError, match="unknown review action"):
        review_belief(store, belief.id, action="nonsense", reason="r")
