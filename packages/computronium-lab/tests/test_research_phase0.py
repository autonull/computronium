"""Phase 0 tests: research schema, budget tiers, structured evidence, audit."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from pathlib import Path
from ceec.models import Scope
from ceec.store import CEECStore
from computronium_lab.research import (
    BUDGET_CAPS,
    BudgetTier,
    CorpusSpec,
    MeasurementBlock,
    MeasurementProtocol,
    StatisticalSummary,
    corpus_root,
    curve_evidence,
    frontier_evidence,
    results_dir,
    run_ledger_audit,
    vector_evidence,
    write_manifest,
)


def _scope() -> Scope:
    return Scope.of(domain="lab", substrate=("digital",), budget="quick")


def test_budget_caps_follow_ladder() -> None:
    assert BUDGET_CAPS[BudgetTier.SMOKE].max_campaigns == 2
    assert BUDGET_CAPS[BudgetTier.QUICK].max_seeds == 3
    assert BUDGET_CAPS[BudgetTier.CERTIFIED].max_epochs_per_campaign is None


def test_protocol_experiment_config_shape() -> None:
    protocol = MeasurementProtocol(problem_class="flat", seeds=(0, 1), epochs=2)
    config = protocol.experiment_config(question="q?", prediction="p.")
    assert config["id"].startswith("X-")
    assert config["design"]["evidence_kind"] == "vector"
    assert config["design"]["seeds"] == [0, 1]
    assert config["metrics"] and config["hard_gates"]


def test_statistical_summary_deterministic() -> None:
    samples = [0.9, 0.85, 0.92]
    first = StatisticalSummary.from_samples("accuracy", samples, seed=1)
    second = StatisticalSummary.from_samples("accuracy", samples, seed=1)
    assert (first.ci_low, first.ci_high) == (second.ci_low, second.ci_high)
    assert first.n == 3 and first.mean == pytest.approx(0.89)
    paired = first.with_paired([0.9, 0.85, 0.92], [0.8, 0.8, 0.8])
    assert paired.paired_p is not None and 0.0 <= paired.paired_p <= 1.0


def test_vector_evidence_structured(tmp_path: Path) -> None:
    store = CEECStore(tmp_path / "db.sqlite3", tmp_path / "artifacts")
    try:
        evidence_id = vector_evidence(
            store,
            _scope(),
            axes=["seed"],
            values=[0.9, 0.85, 0.92],
            values_ref="campaign/spec",
            quality={"seeds": 3},
        )
        evidence = store.get_evidence(evidence_id)
        assert evidence.kind == "vector"
        assert evidence.axes == ["seed"]
        assert evidence.values_ref == "campaign/spec"
    finally:
        store.close()


def test_curve_and_frontier_evidence(tmp_path: Path) -> None:
    store = CEECStore(tmp_path / "db.sqlite3", tmp_path / "artifacts")
    try:
        curve_id = curve_evidence(
            store,
            _scope(),
            history=[{"epoch": 0, "accuracy": 0.5}, {"epoch": 1, "accuracy": 0.9}],
            values_ref="run/1",
        )
        assert store.get_evidence(curve_id).kind == "curve"
        frontier_id = frontier_evidence(
            store,
            _scope(),
            points=[{"accuracy": 0.9, "latency_ms": 5.0}],
            axes=["accuracy", "latency_ms"],
            values_ref="frontier/v1",
        )
        assert store.get_evidence(frontier_id).kind == "frontier"
    finally:
        store.close()


def test_measurement_block_records_missing(tmp_path: Path) -> None:
    store = CEECStore(tmp_path / "db.sqlite3", tmp_path / "artifacts")
    try:
        block = MeasurementBlock(
            problem_class="parity", mechanism="ff_mlp", reason="at-chance ceiling"
        )
        evidence_id = block.record(store, _scope())
        evidence = store.get_evidence(evidence_id)
        assert evidence.kind == "missing"
        assert "at-chance" in (evidence.notes or "")
    finally:
        store.close()


def test_unified_audit_extended_shape(tmp_path: Path) -> None:
    store = CEECStore(tmp_path / "db.sqlite3", tmp_path / "artifacts")
    store.ingest_artifact(b"{}", "research_corpus_summary", {"k": "v"})
    store.close()
    result = run_ledger_audit(tmp_path / "db.sqlite3")
    artifact_types = result["artifact_types"]
    assert isinstance(artifact_types, list)
    assert "research_corpus_summary" in artifact_types
    assert result["campaign_only"] is True
    assert result["x_codes"] == []
    assert "findings" in result


def test_audit_rejects_x_codes(tmp_path: Path) -> None:
    store = CEECStore(tmp_path / "db.sqlite3", tmp_path / "artifacts")
    store.ingest_artifact(b"{}", "validation_campaign", {"probe": "X-FOO-001"})
    store.close()
    result = run_ledger_audit(tmp_path / "db.sqlite3")
    assert result["x_codes"] == ["X-FOO-001"]
    assert result["clean"] is False


def test_paths_and_manifest(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    spec = CorpusSpec(name="v1", problem_classes=("flat",), seeds=(0,))
    protocol = spec.protocol_for("flat")
    assert protocol.seeds == (0,)
    run_dir = results_dir("flat", 0, timestamp="20260913T000000Z")
    assert run_dir.exists()
    manifest = write_manifest(run_dir, {"problem_class": "flat"})
    assert manifest.exists()
    assert corpus_root().exists()
