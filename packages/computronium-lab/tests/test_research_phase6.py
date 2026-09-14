"""Phase 6 tests: cookbook gates, reports, hypothesis calibration."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ceec.store import CEECStore
from computronium_lab.campaign import CampaignReport, MechanismBelief
from computronium_lab.research import (
    HYPOTHESES,
    CookbookEntry,
    CookbookRefusal,
    build_failure_manifesto,
    certify_entry,
    preregister_hypotheses,
    render_cookbook,
    render_manifesto,
    score_hypotheses,
    write_hypothesis_reports,
)

if TYPE_CHECKING:
    from pathlib import Path


def _belief(promoted: bool) -> MechanismBelief:
    report = CampaignReport(
        mechanism="backprop_mlp",
        spec_key="flat",
        seeds=(0, 1, 2),
        accuracies=(0.9, 0.91, 0.89),
        predicted_accuracy=0.91,
        reproduction=True,
        stability=True,
        deployability=True,
        certified=True,
    )
    return MechanismBelief(
        belief_id="B-TEST-001",
        statement="backprop_mlp works",
        mechanism="backprop_mlp",
        campaigns=(report,),
        control_accuracies={"permuted": 0.25},
        evaluation=None,
        promoted=promoted,
        violations=() if promoted else ("gate_failed",),
    )


def test_certify_promoted_belief() -> None:
    entry = certify_entry(
        _belief(True),
        problem_class="flat_classification",
        constraints="digital",
        coordinate={"credit": "bp"},
        known_limitations="none found",
        deployment_notes="export to onnx",
    )
    assert isinstance(entry, CookbookEntry)
    assert entry.mechanism == "backprop_mlp"


def test_certify_refuses_unpromoted() -> None:
    refusal = certify_entry(
        _belief(False),
        problem_class="flat_classification",
        constraints="digital",
        coordinate={},
        known_limitations="",
        deployment_notes="",
    )
    assert isinstance(refusal, CookbookRefusal)
    assert "not promoted" in refusal.reason


def test_certify_boundary_negative() -> None:
    entry = certify_entry(
        None,
        problem_class="sequence_parity",
        constraints="digital",
        coordinate={"credit": "bp"},
        known_limitations="at chance at recorded budgets",
        deployment_notes="do not deploy for parity",
        boundary_belief_id="B-BOUND-001",
    )
    assert isinstance(entry, CookbookEntry)
    assert "boundary" in entry.evidence


def test_render_cookbook_lists_refusals() -> None:
    text = render_cookbook([_belief_entry(), _refusal_entry()])
    assert "Certified entries: 1; refusals: 1." in text


def _belief_entry() -> CookbookEntry:
    entry = certify_entry(
        _belief(True),
        problem_class="flat_classification",
        constraints="digital",
        coordinate={},
        known_limitations="",
        deployment_notes="",
    )
    assert isinstance(entry, CookbookEntry)
    return entry


def _refusal_entry() -> CookbookRefusal:
    refusal = certify_entry(
        None,
        problem_class="flat_classification",
        constraints="digital",
        coordinate={},
        known_limitations="",
        deployment_notes="",
    )
    assert isinstance(refusal, CookbookRefusal)
    return refusal


def test_hypothesis_reports_written(tmp_path: Path) -> None:
    paths = write_hypothesis_reports(tmp_path / "hypotheses")
    assert len(paths) == 6
    assert {p.stem for p in paths} == {h.id for h in HYPOTHESES}
    text = (tmp_path / "hypotheses" / "H24.1.md").read_text(encoding="utf-8")
    assert "Status:" in text and "Protocol" in text


def test_preregister_and_score(tmp_path: Path) -> None:
    store = CEECStore(tmp_path / "db.sqlite3", tmp_path / "artifacts")
    try:
        ids = preregister_hypotheses(store, "T6")
        assert set(ids) == {h.id for h in HYPOTHESES}
        assert store.get_experiment(ids["H24.1"]).status == "pre_registered"
        result = score_hypotheses(
            store,
            ids,
            {"H24.1": ("frontier_grew", True), "H24.4": ("ranked", True)},
        )
        assert set(result["scored"]) == {"H24.1", "H24.4"}
        assert result["scored"]["H24.1"]["brier_score"] is not None
        assert result["report"]["scored_records"] == 2
    finally:
        store.close()


def test_failure_manifesto_empty() -> None:
    manifesto = build_failure_manifesto()
    assert set(manifesto) == {
        "failed_candidates",
        "failed_mutations",
        "failed_transfers",
        "task_class_mismatches",
    }
    text = render_manifesto(manifesto)
    assert "failed_candidates (0)" in text


def test_attempt_promotion_refuses_without_ledger() -> None:
    from computronium_lab import Lab
    from computronium_lab.research import attempt_promotion

    lab = Lab(seed=0)
    spec = lab.specify("flat_classification", "gaussian_blob")
    belief, reason = attempt_promotion(lab, "backprop_mlp", [spec])
    assert belief is None
    assert "ledger" in reason
