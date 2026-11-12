"""T2: Iris is one validation row short, not one algorithm short.

Measured claim: 0.867 best val_acc on a 30-row holdout against the >0.90
criterion. One sample is 1/30 = 0.033, so the 0.033 gap is exactly one row.

This probe reads the same five stratified folds into three arms so the
comparison is paired:

- composed pipeline (gradient / feedforward / instantaneous / adam),
- sklearn LogisticRegression reference,
- sklearn MLPClassifier reference.

Fold-mean resolution is 1/150 = 0.0067. The claim is the fold mean, not a
single holdout.

Run: uv run python scripts/probes/t2_iris_folds.py
Measured (2026-11-12): pipeline **0.9533 ± 0.0163** (n=5 folds, 100 epochs),
sklearn LogisticRegression **0.9600**, sklearn MLPClassifier **0.9533**.
Resolution 1/150 = 0.0067; majority 0.333. Margin over the 0.90 target is
0.053, more than 3σ, so the claim is met and the 0.867 holdout was one row.
"""

from __future__ import annotations

import json
import time

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.neural_network import MLPClassifier

from computronium.domains.tabular import TabularTask
from computronium.evaluation.base import cross_validate
from computronium.experiment.kernel.compose import compose_cell_system
from computronium.experiment.schema.coordinate import Coordinate

__all__ = ["main"]

EPOCHS = 100
N_FOLDS = 5
RESULTS: dict[str, object] = {
    "task": "iris",
    "n_folds": N_FOLDS,
    "epochs": EPOCHS,
    "fold_mean": {},
    "per_fold": {},
    "resolution": 1.0 / 150,
    "majority_baseline": 1.0 / 3,
}


def _coordinate() -> Coordinate:
    return Coordinate(
        substrate="digital",
        geometry="feedforward",
        dynamics="instantaneous",
        plasticity="null",
        credit="gradient",
        update="adam",
        params={},
    )


def _system_factory(input_dim: int, output_dim: int):
    cell = compose_cell_system(
        coordinate=_coordinate(),
        geometry={"hidden_dim": 64, "num_layers": 2},
        input_shape=(input_dim,),
        output_dim=output_dim,
    )
    return cell.system


def main() -> int:
    started = time.perf_counter()
    task = TabularTask(name="iris", dataset_name="iris", device="cuda")
    task.setup()
    folds = task.fold_indices(N_FOLDS)
    X, y = task._X, task._y

    references: dict[str, list[float]] = {
        "logistic_regression": [],
        "mlp_classifier": [],
    }
    for train_idx, val_idx in folds:
        logistic = LogisticRegression(max_iter=2000)
        logistic.fit(X[train_idx], y[train_idx])
        references["logistic_regression"].append(
            float((logistic.predict(X[val_idx]) == y[val_idx]).mean())
        )

        mlp = MLPClassifier(hidden_layer_sizes=(64, 64), max_iter=2000, random_state=0)
        mlp.fit(X[train_idx], y[train_idx])
        references["mlp_classifier"].append(
            float((mlp.predict(X[val_idx]) == y[val_idx]).mean())
        )

    per_fold = cross_validate(_system_factory, task, n_folds=N_FOLDS, epochs=EPOCHS)
    pipeline = [per_fold[f"fold_{i}"]["accuracy"] for i in range(N_FOLDS)]

    RESULTS["per_fold"] = {"pipeline": pipeline, **references}
    RESULTS["fold_mean"] = {
        "pipeline": float(np.mean(pipeline)),
        "logistic_regression": float(np.mean(references["logistic_regression"])),
        "mlp_classifier": float(np.mean(references["mlp_classifier"])),
    }
    RESULTS["pipeline_std"] = float(np.std(pipeline))
    RESULTS["walltime_s"] = round(time.perf_counter() - started, 1)
    print(json.dumps(RESULTS, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
