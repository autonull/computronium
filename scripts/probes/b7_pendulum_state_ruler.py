"""Naive rulers for the B7 scientific task (TODO90).

Builds the offline ``ScientificTask`` pendulum loader and measures the fixed
policies a claim has to beat on the exact split a cell validates on. The
identity (persistence) policy is the natural ruler: it reads the input state
and repeats it.

Measured 2026-11-13: identity MSE 0.04302 (SE 0.00088) on n = 1,000 val rows,
zero/mean 1.33135. The identity arm is registered in
``configs/preregistrations/b7_scientific_pendulum_state_mse.json``.
"""

import math

import torch

from computronium.domains.base import TaskSplit
from computronium.domains.scientific import ScientificTask


def _sample_mse(x: torch.Tensor, y: torch.Tensor) -> torch.Tensor:
    return ((x - y) ** 2).mean(dim=1)


def main() -> None:
    task = ScientificTask(name="pendulum_state", dataset_name="pendulum", device="cpu")
    task.setup()
    x = torch.cat([batch[0] for batch in task.get_dataloader(TaskSplit.VAL)])
    y = torch.cat([batch[1] for batch in task.get_dataloader(TaskSplit.VAL)])

    policies = {
        "identity (persistence)": x,
        "zero": torch.zeros_like(y),
        "val-mean": y.mean(dim=0).expand_as(y),
        "cos/sin-only (omega zeroed)": torch.stack(
            (x[:, 0], x[:, 1], torch.zeros_like(x[:, 2])), dim=1
        ),
    }
    for name, prediction in policies.items():
        per_sample = _sample_mse(prediction, y)
        mean = per_sample.mean().item()
        se = per_sample.std(unbiased=True).item() / math.sqrt(len(per_sample))
        print(f"{name:32s} mse {mean:.5f}  se {se:.5f}  n {len(per_sample)}")

    best = _sample_mse(x, y).mean().item()
    print(f"strongest fixed-policy ruler: identity {best:.5f}")
    print(f"input shape {tuple(x.shape)} target shape {tuple(y.shape)}")


if __name__ == "__main__":
    main()
