"""Probe: does a composed cell train on `digits` through SystemTrainer?

Informed TODO46 §3.1; superseded by `tests/property/test_cell_evaluation_lock.py`,
which asserts the same thing as a gate. Kept for the measured regime, CPU,
1x8x8 digits, feedforward/energy_minimization/fast_weights:

* task setup ~1.0 s (once per process; the evaluator caches it)
* one epoch ~0.06-0.6 s
* train_acc ~0.08-0.12 at 1-2 epochs against a 0.1 chance baseline -- the cell
  trains but the regime is far too short to separate learning from chance
"""

from __future__ import annotations

import time

import torch

from computronium.core.system_trainer import SystemTrainer, SystemTrainerConfig
from computronium.domains.factory import create_task
from computronium.experiment.execution.compose import compose_cell_system
from computronium.experiment.schema.coordinate import Coordinate


def run(task_name: str, credit: str, epochs: int = 1) -> tuple[float, float, float]:
    task = create_task(task_name, device="cpu", quick_mode=True, num_workers=0)
    task.setup()
    shape = task.input_dim
    input_dim = int(torch.tensor(shape).prod().item()) if shape is not None else 0
    loader = task.get_dataloader("train")

    coord = Coordinate(
        substrate="digital",
        geometry="feedforward",
        dynamics="energy_minimization",
        plasticity="fast_weights",
        credit=credit,
        update="euclidean",
        params={},
    )
    cell = compose_cell_system(
        coordinate=coord,
        geometry={},
        input_shape=(input_dim,),
        output_dim=task.output_dim,
    )
    torch.manual_seed(0)
    cfg = SystemTrainerConfig(
        max_epochs=epochs, device="cpu", seed=0, track_flops=False, track_memory=False
    )
    start = time.monotonic()
    with SystemTrainer(cell.system, cfg, loader) as trainer:
        history = trainer.fit()
    wall = time.monotonic() - start
    return history[-1]["train_acc"], history[-1]["train_loss"], wall


if __name__ == "__main__":
    for credit in ("thermodynamic_contrast", "local_contrastive"):
        acc, loss, wall = run("digits", credit)
        print(f"credit={credit} train_acc={acc:.4f} train_loss={loss:.4f} {wall:.2f}s")
