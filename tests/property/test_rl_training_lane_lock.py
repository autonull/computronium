"""Lock: the continuous RL lane updates per step, not per episode (T1).

The harness measured −1184 on Pendulum after 400 episodes while a plain
actor-critic reference reached −123.6 at the same budget. The defect was one
gradient step per episode: 400 episodes bought 400 updates. The continuous
lane now keeps a replay buffer and takes a DDPG update per environment step;
the discrete lane keeps the one-step actor-critic.

Falsified by reverting the continuous lane to a per-episode update: the replay
buffer disappears, so the first assertion fails.
"""

from __future__ import annotations

import torch

from computronium.core.system_trainer.config import SystemTrainerConfig
from computronium.core.system_trainer.rl_trainer import RLSystemTrainer
from computronium.domains.factory import create_task
from computronium.experiment.kernel.compose import compose_cell_system
from computronium.experiment.schema.coordinate import Coordinate


def _cell(input_dim: int, output_dim: int):
    return compose_cell_system(
        coordinate=Coordinate(
            substrate="digital",
            geometry="feedforward",
            dynamics="instantaneous",
            plasticity="null",
            credit="gradient",
            update="adam",
            params={},
        ),
        geometry={"hidden_dim": 32, "num_layers": 2},
        input_shape=(1, input_dim),
        output_dim=output_dim,
    ).system


def _config(episodes: int) -> SystemTrainerConfig:
    return SystemTrainerConfig(
        max_epochs=1,
        device="cpu",
        track_energy=False,
        track_flops=False,
        track_memory=False,
        log_every_n_epochs=0,
        extra={"episodes_per_epoch": episodes},
    )


def test_continuous_lane_updates_from_replay() -> None:
    """Pendulum: each step fills the replay and updates the actor."""
    task = create_task("pendulum", device="cpu", quick_mode=True)
    task.setup()
    task.max_steps = 5
    system = _cell(task.input_dim, task.output_dim)
    trainer = RLSystemTrainer(system=system, config=_config(2), train_data=task)
    import computronium.core.system_trainer.rl_trainer as module

    original = module.DDPG_WARMUP
    module.DDPG_WARMUP = 4
    try:
        before = {
            key: value.detach().clone() for key, value in system.geometry.params.items()
        }
        metrics = trainer._train_episode()
        assert metrics["steps"] == 5
        assert len(trainer._replay) == 5
        assert any(
            not torch.equal(before[key], value)
            for key, value in system.geometry.params.items()
        )
        assert all(
            torch.isfinite(value).all() for value in system.geometry.params.values()
        )
    finally:
        module.DDPG_WARMUP = original


def test_discrete_lane_updates_per_step() -> None:
    """CartPole keeps the one-step actor-critic and trains."""
    task = create_task("cartpole", device="cpu", quick_mode=True)
    task.setup()
    task.max_steps = 5
    system = _cell(task.input_dim, task.output_dim)
    trainer = RLSystemTrainer(system=system, config=_config(2), train_data=task)
    before = {
        key: value.detach().clone() for key, value in system.geometry.params.items()
    }
    metrics = trainer._train_episode()
    assert metrics["steps"] == 5
    assert any(
        not torch.equal(before[key], value)
        for key, value in system.geometry.params.items()
    )
