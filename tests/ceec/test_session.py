"""Session façade closed loop (TODO26 Phase D success criterion)."""

import json

import pytest
from ceec.profile import CORE_CONSTRAINTS, LedgerRole, Profile
from ceec.run import ProbeResult
from ceec.session import ledger

from ceec import models

PROFILE = Profile(
    name="test-session",
    policy_version="26.0",
    constraints=CORE_CONSTRAINTS,
    default_cost={"quick": 1.0, "standard": 4.0, "nightly": 16.0},
    tier_budget={"certified": "nightly", "quick": "quick"},
)


def _scope():
    return models.Scope.of(domain="test", substrate=("digital",), budget="quick")


def _belief(sess):
    scope = _scope()
    artifact = sess.store.ingest_artifact(b"ev", "result")
    ev = sess.store.record_evidence(
        "vector",
        scope,
        artifact_refs=[artifact.id],
        axes=["seed"],
        values_ref=artifact.uri,
        quality={
            "seeds": 3,
            "matched_control": True,
            "evaluation_policy": "single_cycle_v1",
            "defect_audit": "pass",
            "integrity_checks": "pass",
            "reproduction": True,
        },
    )
    sess.store.create_belief("hypothesis", "mechanism", scope, id_="B-S1")
    sess.store._link(
        sess.store._conn, "belief_evidence", "belief_id", "B-S1", "evidence_id", [ev.id]
    )
    sess.store._conn.commit()
    sess.store.update_belief(
        "B-S1",
        models.Probability(low=0.96, high=0.99, point=0.97),
        "low",
        "high",
        "broad",
        "open",
        "bootstrap",
    )
    sess.store.create_goal("viability", "science", id_="G-S1")
    sess.store.revise_goal("G-S1", {"science": 1.0}, scalar_utility=1.0)
    return scope


@pytest.fixture
def sess(tmp_path):
    with ledger(tmp_path / "ledger.sqlite3", PROFILE) as session:
        yield session


def _probe(experiment):
    return ProbeResult(
        label="passed",
        outcome_boolean=True,
        payload={"ok": True, "acc": 0.91},
        axes=("seed",),
        values=(0.91, 0.92, 0.90),
        values_ref="acc",
        quality={
            "seeds": 3,
            "matched_control": True,
            "evaluation_policy": "single_cycle_v1",
            "defect_audit": "pass",
            "integrity_checks": "pass",
            "reproduction": True,
        },
    )


def test_run_closed_loop_promotes(sess):
    scope = _belief(sess)
    draft = sess.experiment(
        question="q",
        prediction="p",
        scope=scope,
        targets=["B-S1"],
        goals=["G-S1"],
        design={
            "seed_plan": [0, 1, 2],
            "evaluation_policy": "e",
            "evidence_kind": "vector",
        },
        tier="certified",
    )
    assert draft.budget == "nightly"
    run = sess.run(draft, _probe, evaluate="promotion")
    assert run.status == "completed"
    assert run.evaluation is not None and run.evaluation.all_passed
    assert sess.store.current_status("B-S1") == "promoted"
    decision = sess.store._conn.execute(
        "SELECT policy_version FROM decisions WHERE id = ?", (run.decision_id,)
    ).fetchone()
    assert decision["policy_version"] == "26.0"


def test_record_result_manual_control(sess):
    scope = _belief(sess)
    draft = sess.experiment(
        question="q2",
        prediction="p2",
        scope=scope,
        targets=["B-S1"],
        design={"seed_plan": [0], "evaluation_policy": "e", "evidence_kind": "vector"},
    )
    run = sess.record_result(draft, _probe(draft))
    assert run.status == "completed"
    assert run.calibration_id is None or run.calibration_id


def test_decide_focus_fallback_native(sess):
    scope = _belief(sess)
    bad = sess.experiment(
        question="bad",
        prediction="p",
        scope=scope,
        targets=["B-S1"],
        controls=(),
    )
    good = sess.experiment(
        question="good",
        prediction="p",
        scope=scope,
        targets=["B-S1"],
        design={"seed_plan": [0], "evaluation_policy": "e", "evidence_kind": "vector"},
    )
    sess.store.pre_register_experiment(bad)
    sess.store.pre_register_experiment(good)
    decision = sess.decide(
        rationale="focus fallback",
        candidate_ids=[bad.id, good.id],
        focus_id=bad.id,
    )
    assert decision.selected_experiment == good.id
    assert "fell back" in decision.rationale
    assert not any(o.get("select_experiment") == bad.id for o in decision.overrides)


def test_close_round_clean(sess):
    _belief(sess)
    report = sess.close_round()
    assert report.clean
    assert "# Ledger Report" in report.markdown


def test_render_writes_files(sess, tmp_path):
    _belief(sess)
    markdown, _data = sess.render(tmp_path / "out" / "report")
    assert (tmp_path / "out" / "report.md").exists()
    assert (tmp_path / "out" / "report.json").exists()
    assert "experiments" in json.loads((tmp_path / "out" / "report.json").read_text())
    assert markdown.startswith("# Ledger Report")


def test_ledger_role_stamped(tmp_path):
    with ledger(tmp_path / "c.sqlite3", PROFILE, role=LedgerRole.CAMPAIGN) as sess:
        assert sess.role == LedgerRole.CAMPAIGN
        row = sess.store._conn.execute(
            "SELECT value FROM ledger_meta WHERE key = 'role'"
        ).fetchone()
        assert row["value"] == "campaign"
