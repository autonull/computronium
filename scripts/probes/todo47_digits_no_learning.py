"""Probe why `digits` does not learn through `cell_record` (TODO47 §6.1).

Chance is 0.1 (10 classes) and every regime measured at or below it, including
`gradient` credit — the backprop-like reference. This probe walks the
evaluation path one stage at a time and reports where the signal dies:

1. the task's own batches (are (x, y) shapes/labels sane? can a linear probe
   on the raw pixels beat chance?),
2. the composed reference cell through the evaluator (what the campaign
   measures), across step sizes.

Measured regime notes live in TODO47 §6.1.
"""

from __future__ import annotations

from typing import Any

import torch

from computronium.experiment.execution.evaluate import evaluate_cell
from computronium.experiment.schema.coordinate import Coordinate, Schedule


def _digits_task():
    from computronium.domains.factory import create_task

    task = create_task("digits", device="cpu", quick_mode=True, num_workers=0)
    task.setup()
    return task


def _linear_probe(train_loader, val_loader, device="cpu") -> float:
    """Can *anything* read class signal from the batches as given?"""
    torch.manual_seed(0)

    def _flatten(loader: Any, xs: list, ys: list) -> None:
        for batch_x, batch_y in loader:
            xs.append(batch_x.reshape(batch_x.size(0), -1))
            ys.append(batch_y)

    xs, ys, vs, vys = [], [], [], []
    _flatten(train_loader, xs, ys)
    _flatten(val_loader, vs, vys)
    x = torch.cat(xs).to(device)
    y = torch.cat(ys).to(device)
    xv = torch.cat(vs).to(device)
    yv = torch.cat(vys).to(device)
    print("probe train tensor:", tuple(x.shape), "val tensor:", tuple(xv.shape))
    model = torch.nn.Linear(x.size(1), int(y.max()) + 1).to(device)
    opt = torch.optim.Adam(model.parameters(), lr=1e-3)
    for _ in range(200):
        opt.zero_grad()
        loss = torch.nn.functional.cross_entropy(model(x), y)
        loss.backward()
        opt.step()
    with torch.no_grad():
        return float((model(xv).argmax(-1) == yv).float().mean())


def _cell(step_size: float) -> Coordinate:
    return Coordinate(
        substrate="real",
        geometry="feedforward",
        dynamics="energy_minimization",
        credit="gradient",
        update="euclidean",
        plasticity="null",
        params={"depth": 2, "hidden_dim": 64, "step_size": step_size},
    )


def main() -> None:
    torch.manual_seed(0)
    task = _digits_task()
    train_loader = task.get_dataloader("train")
    val_loader = task.get_dataloader("val")

    for x, y in train_loader:
        print(
            "first train batch:",
            tuple(x.shape),
            str(x.dtype),
            "labels:",
            (y.min().item(), y.max().item()),
        )
        break
    print("linear probe val_acc:", _linear_probe(train_loader, val_loader))

    for step_size in (1e-5, 3.2e-3, 3.2e-2):
        schedule = Schedule(
            fidelity="L0",
            seed=0,
            n_seeds=1,
            epochs=10,
            batch_limit=0,
            budget_id="probe",
            task_id="digits",
        )
        evaluation = evaluate_cell(
            _cell(step_size),
            schedule,
            device="cpu",
        )
        print(f"step_size={step_size}: metrics={dict(evaluation.metrics)}")


if __name__ == "__main__":
    main()
