"""T8: re-measure graph x target_inversion at the claim-grade budget.

The T3 table's graph row has two error-aware credits (gradient,
random_projections). The named third candidate, ``target_inversion``, measured
0.6842 at 6 epochs against a 0.6579 majority on 38 validation graphs — one
graph is the whole margin (1/38 = 0.026), so one seed cannot decide it.

This probe runs the arm at the budget the geometry itself was measured at
(200 epochs, the MUTAG expressivity probe's regime) with ``gradient`` on the
same task and budget as the positive control: if the control clears the
majority baseline while ``target_inversion`` does not, the verdict is
credit-specific; if both sit near it, the budget is the limit. A 20-epoch
pre-run put *both* arms at the majority baseline, which measured the protocol,
not the credit.

The ruler: 38 held-out graphs, one graph = 0.0263; the task's own class prior
is the baseline.

The companion claim in the same table — graph x ``thermodynamic_contrast`` —
is unreachable through the planner: the declared
``nonlayered_geometry_dynamics`` void constraint admits only instantaneous
dynamics on graph. Composing it directly reproduces the measured break: the
compiled energy settle adds a batch-sized head row block to a node-sized
hidden act (``560x64 + 32x64``), because GraphGeometry pools the node stack
before the head. That is a shape break in the settle contract, not a Dynamo
bug, and it is already declared.

Run: uv run python scripts/probes/t8_graph_third_credit.py
Measured (2026-11-12, MUTAG 188 graphs, mean pooling, hidden 64, CPU, 200
epochs, seeds 0-4, 38 held-out graphs, resolution 1/38 = 0.0263, majority
baseline 0.6579):

    target_inversion   0.6842 +/- 0.0204 (SE)   margin +0.0263 = 1.29 SE
                       seeds 0.684 / 0.763 / 0.658 / 0.658 / 0.658
                       (two seeds above the baseline, three at it)
    gradient           0.7105 +/- 0.0000        margin +0.0526 = 2 graphs
                       (positive control: all five seeds clear)

Verdict: ``target_inversion`` on graph is **marginal, not met**. The 0.6842
reported from one 6-epoch seed was that seed's single extra graph, not a
reproducible credit. The graph row stays at two error-aware credits
(gradient, random_projections); the third is a named verdict, not a defect.

A 20-epoch pre-run put *both* arms exactly at the majority baseline, which
measured the protocol rather than the credit; the geometry's own expressivity
probe needed 200 epochs to reach 0.71-0.74, so the re-measure uses that
regime.
"""

from __future__ import annotations

import json
import time

import torch

from computronium.core.system_trainer.config import SystemTrainerConfig
from computronium.core.system_trainer.graph_trainer import GraphSystemTrainer
from computronium.domains.factory import create_task
from computronium.experiment.kernel.compose import compose_cell_system
from computronium.experiment.schema.coordinate import Coordinate

__all__ = ["main"]

EPOCHS = 200
SEEDS = (0, 1, 2, 3, 4)
CREDITS = ("target_inversion", "gradient")
RESULTS: dict[str, object] = {}


def _cell(task, credit: str):
    input_shape = (
        task.input_dim if isinstance(task.input_dim, tuple) else (1, task.input_dim)
    )
    return compose_cell_system(
        coordinate=Coordinate(
            substrate="digital",
            geometry="graph",
            dynamics="instantaneous",
            plasticity="null",
            credit=credit,
            update="adam",
            params={},
        ),
        geometry={"hidden_dim": 64, "pooling": "mean"},
        input_shape=input_shape,
        output_dim=task.output_dim,
        task=task,
    )


def _measure(task, credit: str) -> dict[str, object]:
    per_seed: list[dict[str, object]] = []
    for seed in SEEDS:
        started = time.perf_counter()
        torch.manual_seed(seed)
        cell = _cell(task, credit)
        config = SystemTrainerConfig(
            max_epochs=EPOCHS,
            device="cpu",
            track_energy=False,
            track_flops=False,
            track_memory=False,
            log_every_n_epochs=0,
        )
        trainer = GraphSystemTrainer(system=cell.system, config=config, train_data=task)
        trainer.fit()
        metrics = task.evaluate(cell.system)
        per_seed.append({
            "seed": seed,
            "accuracy": metrics.accuracy,
            "loss": metrics.loss,
            "majority_baseline": metrics.custom.get("majority_baseline"),
            "last_train_acc": trainer.history[-1].get("train_acc"),
            "walltime_s": round(time.perf_counter() - started, 2),
        })
        print(json.dumps({"credit": credit, **per_seed[-1]}), flush=True)

    accuracies = torch.tensor(
        [row["accuracy"] for row in per_seed], dtype=torch.float64
    )
    baseline_raw = per_seed[0]["majority_baseline"]
    baseline = float(baseline_raw) if isinstance(baseline_raw, int | float) else None
    mean = float(accuracies.mean())
    se = float(accuracies.std(unbiased=True) / len(SEEDS) ** 0.5)
    return {
        "epochs": EPOCHS,
        "seeds": per_seed,
        "mean_accuracy": round(mean, 4),
        "se": round(se, 4),
        "majority_baseline": baseline,
        "margin": None if baseline is None else round(mean - baseline, 4),
        "margin_in_se": None
        if baseline is None or se == 0
        else round((mean - baseline) / se, 2),
    }


def main() -> int:
    started = time.perf_counter()
    task = create_task("graph_classification", device="cpu", quick_mode=True)
    task.setup()
    for credit in CREDITS:
        RESULTS[credit] = _measure(task, credit)
    RESULTS["n_validation_graphs"] = 38
    RESULTS["resolution"] = round(1 / 38, 4)
    RESULTS["walltime_s"] = round(time.perf_counter() - started, 1)
    print(json.dumps(RESULTS, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
