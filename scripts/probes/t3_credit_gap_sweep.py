"""T3: fill the table's named gaps, one arm per missing (geometry, credit).

The store scan (``t3_credit_breadth.py``) leaves four geometries below three
error-aware credits. Each gap has a declared-legal credit that the stores never
measured; this probe measures exactly those, nothing else:

    attention        gradient, random_projections
    nca              random_projections
    spatial_lattice  gradient, random_projections
    graph            target_inversion

Digits (8×8, 10 classes) keeps the vision arms cheap; graph_classification
(MUTAG) keeps the graph arm cheap. One seed, two epochs: the table asks
whether a credit works per geometry, not for a claim-grade mean.

Run: uv run python scripts/probes/t3_credit_gap_sweep.py
Measured (2026-11-12, 2 epochs, 1 seed, digits 8x8 / MUTAG):
- attention/gradient **0.9472**, spatial_lattice/gradient **0.9361** — both
  close their geometry's third slot (chance 0.10, majority ~0.10);
- attention, nca, spatial_lattice x random_projections: **cannot train** —
  the layered-FA contract returns all-zero pseudo-gradients for every weight
  (38 / 3 / 98 weights), so the gap is dispatch, not accuracy. TODO89 T7
  widened the measurement to conv (5 weights) and ntm (7) and declared the
  rule: `random_projections_layered_geometry` voids those four. **T9
  supersedes the nca line**: the declared cell fold trains it at 0.8907
  (`t9_nca_cell_fa.py`).
- graph/target_inversion 0.6316 at 2 epochs, **0.6842 at 6 epochs** vs 0.6579
  majority (38 val graphs, one graph = 0.026) — marginal, not met;
  graph/pc_alm 0.3421 (below majority); graph/thermodynamic_contrast is
  unreachable: the declared `nonlayered_geometry_dynamics` void admits only
  instantaneous dynamics on graph, and composing it directly breaks the
  settle shape (a batch-sized head block added to a node-sized hidden act).

Conclusion: attention and spatial_lattice reach 3; nca has 2 after T9's cell
fold (gradient + random_projections, `t9_nca_cell_fa.py`); graph has gradient +
random_projections (target_inversion re-measured at n=5 in
`t8_graph_third_credit.py`: 0.6842 +/- 0.0204, +1.29 SE over majority —
marginal, not met).
"""

from __future__ import annotations

import json
import time

import torch

from computronium.core.system_trainer.config import SystemTrainerConfig
from computronium.core.system_trainer.graph_trainer import GraphSystemTrainer
from computronium.core.system_trainer.train_task import train_on_task
from computronium.domains.factory import create_task
from computronium.experiment.kernel.compose import compose_cell_system
from computronium.experiment.schema.coordinate import Coordinate

__all__ = ["main"]

EPOCHS = 2
RESULTS: dict[str, object] = {}


def _coordinate(geometry: str, credit: str, dynamics: str) -> Coordinate:
    return Coordinate(
        substrate="digital",
        geometry=geometry,
        dynamics=dynamics,
        plasticity="null",
        credit=credit,
        update="adam",
        params={},
    )


def _train(system, task, geometry: str) -> None:
    config = SystemTrainerConfig(
        max_epochs=EPOCHS,
        device="cpu",
        track_energy=False,
        track_flops=False,
        track_memory=False,
        log_every_n_epochs=1,
    )
    if geometry == "graph":
        GraphSystemTrainer(system=system, config=config, train_data=task).fit()
    else:
        train_on_task(lambda input_dim, output_dim: system, task, config)


def main() -> int:
    arms = (
        ("attention", "gradient", "digits", "instantaneous"),
        ("attention", "random_projections", "digits", "instantaneous"),
        ("nca", "random_projections", "digits", "instantaneous"),
        ("spatial_lattice", "gradient", "digits", "instantaneous"),
        ("spatial_lattice", "random_projections", "digits", "instantaneous"),
        ("graph", "target_inversion", "graph_classification", "instantaneous"),
        ("graph", "pc_alm", "graph_classification", "instantaneous"),
        (
            "graph",
            "thermodynamic_contrast",
            "graph_classification",
            "energy_minimization",
        ),
    )
    started = time.perf_counter()
    for geometry, credit, task_name, dynamics in arms:
        torch.manual_seed(0)
        task = create_task(task_name, device="cpu", quick_mode=True)
        task.setup()
        input_shape = (
            task.input_dim if isinstance(task.input_dim, tuple) else (1, task.input_dim)
        )
        cell = compose_cell_system(
            coordinate=_coordinate(geometry, credit, dynamics),
            geometry=(
                {"hidden_dim": 64, "pooling": "mean"}
                if geometry == "graph"
                else {"hidden_dim": 64}
            ),
            input_shape=input_shape,
            output_dim=task.output_dim,
            task=task if geometry == "graph" else None,
        )
        key = f"{geometry}/{credit}"
        try:
            _train(cell.system, task, geometry)
            metrics = task.evaluate(cell.system)
            RESULTS[key] = {
                "task": task_name,
                "accuracy": metrics.accuracy,
                "majority_baseline": metrics.custom.get("majority_baseline"),
                "loss": metrics.loss,
            }
        except Exception as error:  # ruff: ignore[blind-except] - a failed arm is a named gap
            RESULTS[key] = {"task": task_name, "error": str(error)[:200]}
        print(f"{key}: {RESULTS[key]}", flush=True)
    RESULTS["walltime_s"] = round(time.perf_counter() - started, 1)
    print(json.dumps(RESULTS, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
