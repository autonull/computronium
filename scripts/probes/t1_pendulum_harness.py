"""T1b: reproduce the harness number beside the reference.

The reference (``t1_pendulum_reference.py``) reaches −123.6 at 400 episodes,
so 400 episodes is not the limit. This probe trains the canonical harness cell
on the same budget and reports its deterministic evaluation, so the gap is a
harness number beside a reference number rather than an inference.

Run: uv run python scripts/probes/t1_pendulum_harness.py
Measured (2026-11-12): **−161.2 ± 25.3** across n=3 training seeds
(−133.9 / −165.9 / −183.8; 20 deterministic episodes, 400 training episodes)
after the per-step continuous lane; the one-update-per-episode lane measured
−6604.4 on the same command. Reference: −123.6 at the same budget.
"""

from __future__ import annotations

import json
import os
import time

import torch

from computronium.core.system_trainer.config import SystemTrainerConfig
from computronium.core.system_trainer.rl_trainer import RLSystemTrainer
from computronium.domains.factory import create_task
from computronium.experiment.kernel.compose import compose_cell_system
from computronium.experiment.schema.coordinate import Coordinate

__all__ = ["main"]

EPISODES = 400
EPISODES_PER_EPOCH = 10
EVAL_EPISODES = 20
RESULTS: dict[str, object] = {
    "budget_episodes": EPISODES,
    "episodes_per_epoch": EPISODES_PER_EPOCH,
    "eval_episodes": EVAL_EPISODES,
}


def main() -> int:
    seed = int(os.environ.get("T1_SEED", "0"))
    torch.manual_seed(seed)
    started = time.perf_counter()
    task = create_task("pendulum", device="cpu", quick_mode=True)
    task.setup()
    cell = compose_cell_system(
        coordinate=Coordinate(
            substrate="digital",
            geometry="feedforward",
            dynamics="instantaneous",
            plasticity="null",
            credit="gradient",
            update="adam",
            params={},
        ),
        geometry={"hidden_dim": 64, "num_layers": 2},
        input_shape=(task.input_dim,),
        output_dim=task.output_dim,
    )
    config = SystemTrainerConfig(
        max_epochs=EPISODES // EPISODES_PER_EPOCH,
        device="cpu",
        seed=seed,
        track_energy=False,
        track_flops=False,
        track_memory=False,
        log_every_n_epochs=10,
        extra={"episodes_per_epoch": EPISODES_PER_EPOCH},
    )
    trainer = RLSystemTrainer(system=cell.system, config=config, train_data=task)
    history = trainer.fit()
    metrics = task.evaluate(cell.system, n_episodes=EVAL_EPISODES)
    RESULTS["seed"] = seed
    RESULTS["harness_mean_reward"] = metrics.custom["mean_reward"]
    RESULTS["harness_std_reward"] = metrics.custom["std_reward"]
    RESULTS["train_reward_last"] = history[-1].get("reward") if history else None
    RESULTS["walltime_s"] = round(time.perf_counter() - started, 1)
    print(json.dumps(RESULTS, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
