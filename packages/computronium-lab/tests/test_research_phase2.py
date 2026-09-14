"""Phase 2 tests: evolution surface, frontier archive, adapters, purity."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from pathlib import Path
from computronium_lab import (
    EvolutionBudget,
    EvolutionSpec,
    FrontierArchive,
    Lab,
)
from computronium_lab.research import (
    BudgetTier,
    mirror_hypotheses,
    mirror_proposals,
    seed_genomes_from_proposals,
)
from computronium_lab.synthesis.engine import synthesize as engine_synthesize


def _lab(record_ledger: str | None = None) -> Lab:
    return Lab(seed=0, record_ledger=record_ledger)


def _spec(lab: Lab):
    return lab.specify("flat_classification", "gaussian_blob")


def _smoke_spec() -> EvolutionSpec:
    return EvolutionSpec(
        population=2,
        generations=1,
        seed_candidates=("backprop_mlp", "ff_mlp"),
        objectives=("accuracy", "stability"),
        budget=EvolutionBudget.smoke(),
        tier=BudgetTier.SMOKE,
        seed=0,
        run_id="TESTSMOKE",
    )


def test_plan_dry_run_no_training() -> None:
    lab = _lab()
    plan = lab.plan_evolution(_spec(lab), _smoke_spec())
    assert len(plan.genomes) == 2
    assert all(admitted for _, admitted, _ in plan.admission)
    assert plan.expected_campaigns == 2
    assert plan.run_id == "TESTSMOKE"


def test_plan_rejects_unknown_seed() -> None:
    lab = _lab()
    bad = EvolutionSpec(seed_candidates=("no_such_row",))
    with pytest.raises(ValueError, match="not cataloged"):
        lab.plan_evolution(_spec(lab), bad)


def test_run_evolution_smoke_no_ledger(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    lab = _lab()
    report = lab.run_evolution(lab.plan_evolution(_spec(lab), _smoke_spec()))
    assert len(report.generation_summaries) == 1
    summary = report.generation_summaries[0]
    assert len(summary.evaluated) == 2
    assert report.lineage
    assert report.frontier_points
    assert report.ledger["experiments"] == []
    assert report.to_dict()["run_id"] == "TESTSMOKE"


def test_run_evolution_smoke_ledger(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    lab = _lab(str(tmp_path / "ledger.sqlite3"))
    spec = lab.specify("flat_classification", "gaussian_blob")
    evolution = EvolutionSpec(
        population=2,
        generations=1,
        seed_candidates=("backprop_mlp", "ff_mlp"),
        objectives=("accuracy", "stability"),
        budget=EvolutionBudget.smoke(),
        tier=BudgetTier.SMOKE,
        seed=0,
        run_id="TESTLEDGER",
    )
    report = lab.run_evolution(lab.plan_evolution(spec, evolution))
    assert len(report.ledger["experiments"]) == 1
    assert len(report.ledger["decisions"]) == 1
    assert report.ledger["artifacts"]
    assert report.calibration and report.calibration[0]["brier_score"] is not None
    from computronium_lab import ledger_audit

    audit = ledger_audit(tmp_path / "ledger.sqlite3")
    assert audit["campaign_only"] is True
    assert audit["x_codes"] == []
    assert audit["clean"] is True


def test_frontier_archive_persists(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    lab = _lab()
    spec = _spec(lab)
    lab.run_evolution(lab.plan_evolution(spec, _smoke_spec()))
    archive = FrontierArchive(spec)
    assert len(archive.points) == 2
    assert set(archive.measured_accuracy()) == {"backprop_mlp", "ff_mlp"}
    lab_result = lab.synthesize(spec, include_evolved=True)
    assert lab_result.name in {"backprop_mlp", "ff_mlp"}


def test_synthesize_frontier_provenance() -> None:
    lab = _lab()
    spec = _spec(lab)
    result = engine_synthesize(spec, frontier={"ff_mlp": 0.999})
    assert result.name == "ff_mlp"
    assert any("frontier_archive" in token for token in result.provenance)


def test_resume_offset_skips(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    lab = _lab()
    base = _smoke_spec()
    resumed = EvolutionSpec(
        population=base.population,
        generations=1,
        seed_candidates=base.seed_candidates,
        objectives=base.objectives,
        budget=base.budget,
        tier=base.tier,
        seed=base.seed,
        run_id="TESTRESUME",
        start_generation=1,
    )
    report = lab.run_evolution(lab.plan_evolution(_spec(lab), resumed))
    assert report.generation_summaries == ()


def test_compartment_purity() -> None:
    import pathlib

    root = pathlib.Path("computronium/autoscientist")
    assert root.is_dir()
    for path in root.glob("*.py"):
        text = path.read_text(encoding="utf-8")
        assert "import ceec" not in text and "from ceec" not in text, path
    kernel = pathlib.Path(
        "packages/computronium-lab/src/computronium_lab/research/evolution.py"
    )
    kernel_text = kernel.read_text(encoding="utf-8")
    assert "autoscientist" not in kernel_text


def test_adapters_mirror_and_seed(tmp_path: Path) -> None:
    from types import SimpleNamespace

    from ceec.store import CEECStore

    store = CEECStore(tmp_path / "db.sqlite3", tmp_path / "artifacts")
    try:
        proposals = [
            SimpleNamespace(
                hypothesis="mlp width helps",
                model="backprop_mlp variant",
                task="mnist",
                justification="wider is better",
                expected_outcome="higher accuracy",
                priority=0.8,
                tags=["autoscientist"],
            ),
            SimpleNamespace(
                hypothesis="unknown thing",
                model="quantum_dream",
                task="mnist",
                justification="?",
                expected_outcome="?",
                priority=0.9,
                tags=["autoscientist"],
            ),
        ]
        experiment_ids = mirror_proposals(store, proposals, run_id="T1")
        assert len(experiment_ids) == 2
        assert store.get_experiment(experiment_ids[0]).status == "pre_registered"
        belief_ids = mirror_hypotheses(
            store,
            [SimpleNamespace(statement="width helps", confidence=0.7)],
            run_id="T1",
        )
        assert len(belief_ids) == 1
        lab = _lab()
        genomes, skipped = seed_genomes_from_proposals(proposals, _spec(lab), limit=4)
        assert [g.mechanism for g in genomes] == ["backprop_mlp"]
        assert len(skipped) == 1
    finally:
        store.close()
