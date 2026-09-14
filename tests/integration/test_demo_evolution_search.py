"""D24 — Gallery 3.0: budgeted evolution over mechanism coordinates.

The research surface (TODO24 Phase 2) as a gallery demo: dry-run plan →
two smoke generations with campaign-backed fitness → measured frontier
with hypervolume growth, plus smoke continual and substrate-transfer
panels from the same ledger-backed Lab. Everything is deterministic by
construction — fixed seed, single torch thread, fixed run id, hermetic
archive (tmp cwd) — and measured accuracies are rounded to 1e-4 in the
record (the lock hashes at 1e-6; exact values live in the ledger).
Walltime is printed, never recorded.
"""

from __future__ import annotations

import time

import torch
from computronium_lab import (
    EvolutionBudget,
    EvolutionSpec,
    Lab,
    ledger_audit,
)
from computronium_lab.research import BudgetTier

from computronium.visualization._demo_api import (
    bars_panel,
    figure_spec,
    lines_panel,
)

SEED = 0
RUN_ID = "D24DEMO"

SEED_CANDIDATES = ("backprop_mlp", "ff_mlp")


def _round4(value: float) -> float:
    return round(float(value), 4)


def test_demo_evolution_search(emit_run_record, tmp_path, monkeypatch) -> None:
    previous_threads = torch.get_num_threads()
    torch.set_num_threads(1)
    torch.manual_seed(SEED)
    monkeypatch.chdir(tmp_path)
    try:
        record = _run_demo(tmp_path)
    finally:
        torch.set_num_threads(previous_threads)
    emit_run_record("D24", "evolution_search", record)

    assert record["generations"] == 2
    assert record["audit_clean"] is True
    assert record["evaluated_total"] >= 4
    assert record["frontier_size"] >= 1
    assert record["hypervolume_growth"][-1] >= record["hypervolume_growth"][0]
    assert record["lineage_links"] >= 1


def _run_demo(tmp_path) -> dict:
    t0 = time.perf_counter()
    lab = Lab(seed=SEED, record_ledger=str(tmp_path / "d24.sqlite3"))
    spec = lab.specify("flat_classification", "gaussian_blob")
    plan = lab.plan_evolution(
        spec,
        EvolutionSpec(
            population=3,
            generations=2,
            seed_candidates=SEED_CANDIDATES,
            objectives=("accuracy", "stability"),
            budget=EvolutionBudget(
                max_campaigns=6, max_epochs_per_campaign=1, max_seeds=1
            ),
            tier=BudgetTier.SMOKE,
            seed=SEED,
            run_id=RUN_ID,
        ),
    )
    report = lab.run_evolution(plan)
    audit = ledger_audit(tmp_path / "d24.sqlite3")
    continual_bars = _continual_panel(lab)
    transfer_bars, transfer_ranking = _transfer_panel(lab)
    walltime_s = time.perf_counter() - t0
    print(f"D24 smoke evolution + panels walltime: {walltime_s:.1f}s")
    return _assemble_record(
        report, audit, continual_bars, transfer_bars, transfer_ranking
    )


def _continual_panel(lab) -> dict[str, float]:
    continual = lab.benchmark_continual(
        mechanism="backprop_mlp",
        curriculum="two_task_switch",
        modes=("temporal",),
        controls=("frozen_no_psi",),
        seeds=(SEED,),
    )
    return {
        arm.arm: _round4(arm.metric_values["accuracy"][0])
        for arm in continual.arms
        if arm.metric_values.get("accuracy")
    }


def _transfer_panel(lab) -> tuple[dict[str, float], list[str]]:
    transfer = lab.benchmark_substrate_transfer(
        mechanism="backprop_mlp",
        source_substrate="digital",
        target_constraints=("digital", "ternary"),
        seeds=(SEED,),
    )
    bars = {score.target: _round4(score.accuracy) for score in transfer.scores}
    return bars, list(transfer.ranking)


def _assemble_record(
    report, audit, continual_bars, transfer_bars, transfer_ranking
) -> dict:

    accuracy_bars: dict[str, dict[str, float]] = {}
    best_curve: list[float] = []
    for summary in report.generation_summaries:
        group = f"gen{summary.generation}"
        accuracy_bars[group] = {}
        best = 0.0
        for evaluated in summary.evaluated:
            accuracy = _round4(evaluated["objectives"]["accuracy"])
            accuracy_bars[group][evaluated["mechanism"]] = accuracy
            best = max(best, accuracy)
        best_curve.append(best)
    hypervolume_growth = [0.0] + [
        _round4(summary.hypervolume) for summary in report.generation_summaries
    ]
    lineage_links = sum(len(parents) for parents in report.lineage.values())

    record: dict = {
        "seed": SEED,
        "seed_candidates": list(SEED_CANDIDATES),
        "generations": len(report.generation_summaries),
        "accuracy_bars": accuracy_bars,
        "best_accuracy_curve": best_curve,
        "hypervolume_growth": hypervolume_growth,
        "frontier_size": len(report.frontier_points),
        "evaluated_total": sum(
            len(summary.evaluated) for summary in report.generation_summaries
        ),
        "lineage_links": lineage_links,
        "lineage": {
            digest: list(parents) for digest, parents in report.lineage.items()
        },
        "negative_kinds": sorted({
            negative["kind"] for negative in report.negative_results
        }),
        "audit_clean": bool(audit["clean"]),
        "continual": continual_bars,
        "transfer": transfer_bars,
        "transfer_ranking": list(transfer_ranking),
    }
    record["figure"] = figure_spec(
        "D24 — smoke evolution: measured accuracy, frontier growth, "
        "continual and transfer panels",
        bars_panel(
            accuracy_bars,
            ylabel="measured accuracy",
            title="evolution generations",
        ),
        lines_panel(
            {
                "hypervolume": hypervolume_growth,
                "best_accuracy": [hypervolume_growth[0], *best_curve],
            },
            xlabel="generation",
            ylabel="hypervolume / best accuracy",
        ),
        bars_panel(
            {"two_task_switch": continual_bars},
            ylabel="post-switch accuracy",
            title="continual",
        ),
        bars_panel(
            {"backprop_mlp": transfer_bars},
            ylabel="transfer accuracy",
            title="substrate transfer",
        ),
    )
    return record
