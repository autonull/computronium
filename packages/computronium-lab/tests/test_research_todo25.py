"""TODO25 Phase C/D: trainable_on catalog field, flat_classification_hard
corpus variant, ledger rendering, and the research one-shot API."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

import pytest

if TYPE_CHECKING:
    from pathlib import Path
from computronium_lab import Lab
from computronium_lab.research.autopoiesis import (
    CampaignFitness,
    CoordinateGenome,
    NotTrainableError,
    ResearchConstitution,
)
from computronium_lab.research.corpus import (
    CLASS_BY_NAME,
    MeasurementRunner,
    problem_class_defaults,
)
from computronium_lab.research.reports import render_ledger
from computronium_lab.research.schema import BUDGET_CAPS, BudgetTier
from computronium_lab.synthesis.catalog import CATALOG
from computronium_lab.synthesis.spec import Constraints, ProblemSpec

from computronium.validation.statistics import spearman_rho

FLAT_SPEC = ProblemSpec(
    task="flat_classification",
    dataset="gaussian_blob",
    constraints=Constraints(),
)
HARD_SPEC = ProblemSpec(
    task="flat_classification_hard",
    dataset="gaussian_blob_hard",
    constraints=Constraints(),
    input_dim=64,
    num_classes=8,
)

NOT_CAMPAIGN_TRAINABLE_ON_FLAT = ("temporal_psi_task_switcher", "nca_predictor")


def test_catalog_rows_declare_trainable_on() -> None:
    known = set(CLASS_BY_NAME)
    for row in CATALOG:
        unknown = set(row.trainable_on) - known
        assert not unknown, f"{row.name} claims unknown tasks {unknown}"
    psi = next(c for c in CATALOG if c.name == "temporal_psi_task_switcher")
    assert psi.trainable_on == frozenset()
    assert next(c for c in CATALOG if c.name == "nca_predictor").trainable_on == {
        "nca_state_prediction"
    }


@pytest.mark.parametrize("mechanism", NOT_CAMPAIGN_TRAINABLE_ON_FLAT)
def test_campaign_fitness_raises_structured_not_trainable(mechanism: str) -> None:
    fitness = CampaignFitness(FLAT_SPEC)
    genome = CoordinateGenome.seed(mechanism, FLAT_SPEC)
    with pytest.raises(NotTrainableError, match="trainable_on"):
        fitness.evaluate(genome, Lab(), seeds=(0,), epochs=1)


def test_constitution_admission_rejects_untrainable() -> None:
    constitution = ResearchConstitution(FLAT_SPEC, BUDGET_CAPS[BudgetTier.QUICK])
    genome = CoordinateGenome.seed("temporal_psi_task_switcher", FLAT_SPEC)
    admitted, reason = constitution.evaluate(genome.genome())
    assert not admitted and "no training path" in reason
    backprop = CoordinateGenome.seed("backprop_mlp", FLAT_SPEC)
    admitted, _ = constitution.evaluate(backprop.genome())
    assert admitted


def test_measurement_runner_blocks_before_build(tmp_path: Path) -> None:
    lab = Lab(record_ledger=str(tmp_path / "ledger.sqlite3"))
    report = MeasurementRunner(lab).run(
        "flat_classification",
        ["temporal_psi_task_switcher", "nca_predictor"],
        seeds=(0,),
        epochs=1,
        run_id="t25-block",
    )
    reasons = [b.reason for b in report.blocks]
    assert len(reasons) == 2 and all("no training path" in r for r in reasons)


def test_hard_problem_class_registered_and_runs(tmp_path: Path) -> None:
    assert problem_class_defaults("flat_classification_hard") == {
        "task": "flat_classification_hard",
        "dataset": "gaussian_blob_hard",
        "input_dim": 64,
        "num_classes": 8,
    }
    lab = Lab()
    report = MeasurementRunner(lab).run(
        "flat_classification_hard",
        ["backprop_mlp"],
        seeds=(0,),
        epochs=1,
        run_id="t25-hard",
    )
    arm = report.arms[0]
    accuracy = arm.summaries["accuracy"]
    assert 0.0 <= accuracy.mean <= 1.0
    assert arm.metric_values["accuracy"]


def test_hard_campaign_fitness_path() -> None:
    fitness = CampaignFitness(HARD_SPEC)
    genome = CoordinateGenome.seed("backprop_mlp", HARD_SPEC)
    evaluation = fitness.evaluate(genome, Lab(), seeds=(0,), epochs=1)
    assert 0.0 <= evaluation.objectives["accuracy"] <= 1.0


def test_spearman_rho_matches_scipy_conventions() -> None:
    assert spearman_rho([1, 2, 3], [2, 4, 6]) == pytest.approx(1.0)
    assert spearman_rho([1, 2, 3], [6, 4, 2]) == pytest.approx(-1.0)
    assert spearman_rho([1, 1, 1], [2, 3, 4]) == 0.0


def _seeded_store(path: Path):
    from ceec.store import CEECStore

    from ceec import builders, models

    store = CEECStore(path / "ledger.sqlite3", path / "artifacts")
    scope = models.Scope.of(domain="test", substrate=("digital",), budget="quick")
    draft = builders.experiment(
        id_="X-RENDER-001",
        question="q?",
        prediction="p",
        scope=scope,
        prediction_probability=(0.4, 0.8, 0.6),
    )
    from ceec.run import ProbeResult, run_experiment

    run_experiment(
        store,
        draft,
        lambda _e: ProbeResult(
            label="ok",
            outcome_boolean=True,
            payload={"x": 1},
            axes=("seed",),
            values=(0.5, 0.6),
            values_ref="t/accs",
            quality={"seeds": 2, "matched_control": False, "evaluation_policy": "v1"},
        ),
    )
    return store


def test_render_ledger(tmp_path: Path) -> None:
    store = _seeded_store(tmp_path)
    try:
        markdown, data = render_ledger(store)
    finally:
        store.close()
    assert "# Ledger Report" in markdown
    experiments = cast("dict[str, object]", data["experiments"])
    calibration = cast("dict[str, object]", data["calibration"])
    decisions = cast("dict[str, object]", data["decisions"])
    assert experiments["completed"] == ["X-RENDER-001"]
    assert calibration["scored_records"] == 1
    assert cast("dict[str, object]", decisions["audit"])["decisions"] == 1


def test_research_report_one_shot(tmp_path: Path) -> None:
    lab = Lab(record_ledger=str(tmp_path / "ledger.sqlite3"))
    report = lab.research_report(HARD_SPEC, tier="quick")
    assert report["spec_key"] == HARD_SPEC.key()
    arms = cast("dict[str, object]", report["corpus_arms"])
    assert "backprop_mlp" in cast("tuple[str, ...]", arms["trainable"])
    assert "temporal_psi_task_switcher" in cast(
        "tuple[str, ...]", arms["expected_blocks"]
    )
    assert cast("dict[str, object]", report["synthesis"])["mechanism"]
    plan = cast("dict[str, object]", report["evolution_plan"])
    assert cast("int", plan["expected_campaigns"]) >= 1


def test_research_report_spec_key_roundtrip(tmp_path: Path) -> None:
    lab = Lab()
    report = lab.research_report(FLAT_SPEC.key())
    assert report["spec_key"] == FLAT_SPEC.key()
    with pytest.raises(ValueError, match="not a ProblemSpec key"):
        lab.research_report("not-a-key")


def test_research_report_writes_ledger(tmp_path: Path) -> None:
    from ceec.store import CEECStore

    db = tmp_path / "ledger.sqlite3"
    store = CEECStore(db, tmp_path / "artifacts")
    store.close()
    lab = Lab(record_ledger=str(db))
    report = lab.research_report(path=tmp_path / "reports")
    assert "ledger" in report
    assert (tmp_path / "reports" / "ledger_report.md").exists()
    assert (tmp_path / "reports" / "ledger_report.json").exists()
