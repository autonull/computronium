"""Phase 3 tests: corpus problem classes, protocol runner, re-measurement."""

from __future__ import annotations

from typing import TYPE_CHECKING

from computronium_lab import Lab
from computronium_lab.research import (
    CLASS_BY_NAME,
    BudgetTier,
    MeasurementRunner,
    remeasure_catalog,
)

if TYPE_CHECKING:
    from pathlib import Path

    import pytest


def _runner(tier: BudgetTier = BudgetTier.QUICK) -> MeasurementRunner:
    return MeasurementRunner(Lab(seed=0), tier=tier)


def test_problem_classes_registered() -> None:
    assert set(CLASS_BY_NAME) == {
        "flat_classification",
        "flat_classification_hard",
        "sequence_last_symbol",
        "sequence_threshold",
        "sequence_parity",
        "nca_state_prediction",
        "continual_switch",
        "substrate_transfer",
    }
    for cls in CLASS_BY_NAME.values():
        assert isinstance(cls, type)


def test_flat_runner_smoke(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    report = _runner().run(
        "flat_classification",
        ("backprop_mlp",),
        seeds=(0,),
        epochs=1,
        run_id="CORPUSTEST",
    )
    assert report.problem_class == "flat_classification"
    assert len(report.arms) == 1
    arm = report.arms[0]
    assert arm.metric_values["accuracy"] and len(arm.metric_values["accuracy"]) == 1
    summary = arm.summaries["accuracy"]
    assert summary.n == 1 and summary.paired_p is not None
    assert report.manifest_paths


def test_sequence_runner_smoke(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    report = _runner().run(
        "sequence_last_symbol",
        ("ntm_sequence",),
        seeds=(0,),
        epochs=2,
        run_id="SEQTEST",
    )
    arm = report.arms[0]
    assert "accuracy" in arm.metric_values
    assert "chance" in arm.metric_values


def test_nca_runner_smoke(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    report = _runner().run(
        "nca_state_prediction",
        ("nca_predictor",),
        seeds=(0,),
        epochs=1,
        run_id="NCATEST",
    )
    arm = report.arms[0]
    assert "cell_accuracy" in arm.metric_values


def test_continual_runner_smoke(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    report = _runner().run(
        "continual_switch",
        ("temporal", "frozen_no_psi"),
        seeds=(0,),
        epochs=1,
        run_id="CONTTEST",
    )
    by_arm = {arm.arm: arm for arm in report.arms}
    assert set(by_arm) == {"temporal", "frozen_no_psi"}
    assert by_arm["temporal"].metric_values["theta_invariant"] == (1.0,)


def test_substrate_runner_smoke(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    report = _runner().run(
        "substrate_transfer",
        ("digital", "ternary"),
        seeds=(0,),
        epochs=1,
        run_id="SUBTEST",
    )
    by_arm = {arm.arm: arm for arm in report.arms}
    assert by_arm["digital"].metric_values["fidelity"] == (0.0,)
    assert by_arm["ternary"].metric_values["accuracy"][0] >= 0.0


def test_remeasure_subset_blocks_unconstructible(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    lab = Lab(seed=0)
    reports = remeasure_catalog(
        lab,
        ["sequence_last_symbol"],
        mechanisms=["ntm_sequence", "backprop_mlp"],
        seeds=(0,),
        epochs=1,
        run_id="REMEASURE",
    )
    report = reports["sequence_last_symbol"]
    assert {arm.arm for arm in report.arms} == {"ntm_sequence", "backprop_mlp"}
    assert report.blocks, "expected blocks for rows failing the sequence path"


def test_corpus_ledger_records(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    lab = Lab(seed=0, record_ledger=str(tmp_path / "corpus.sqlite3"))
    MeasurementRunner(lab).run(
        "flat_classification",
        ("backprop_mlp",),
        seeds=(0,),
        epochs=1,
        run_id="LEDGERT",
    )
    from computronium_lab import ledger_audit

    audit = ledger_audit(tmp_path / "corpus.sqlite3")
    assert audit["campaign_only"] is True
    assert audit["x_codes"] == []
