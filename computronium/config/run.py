"""Run a YAML ``RunConfig`` end to end.

``run_from_runconfig`` lived in ``core/trainer.py`` until Sprint 7.6.10
removed that module's trainer, and ``analysis/ablation.py`` -- documented in
the README as the home of leave-one-out and Sobol reporting -- has been
unimportable ever since because it still called it. The replacement is the
same three steps every other entry point takes: name the learning rule, name
the task, call :func:`~computronium.core.system_trainer.train_task.train_task`.

The mapping is one-to-one with the config's own sections, so an ablation over
a ``RunConfig`` dimension and a sweep over the same dimension train the same
system.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from computronium.config.omegaconf import RunConfig

__all__ = ["run_run_config"]


def run_run_config(config: RunConfig) -> dict[str, float]:
    """Train the system ``config`` describes and return its final metrics.

    The learning rule comes from ``optimizer.mode`` (the section that already
    names it), the geometry from ``model``'s depth and width, and the epoch
    length from ``trainer.batches_per_epoch``.

    Raises:
        KeyError: The config names a learning rule the zoo does not have, with
            the names it does have in the message.
    """
    from computronium.core.rules import rule_for, rule_system
    from computronium.core.system_trainer.train_task import (
        final_metrics,
        train_task,
    )
    from computronium.utils import seed_everything

    rule = rule_for(config.optimizer.mode or config.model.name)
    seed_everything(config.seed, config.device)
    history = train_task(
        lambda input_dim, output_dim: rule_system(
            rule,
            input_dim,
            output_dim,
            hidden_dims=(config.model.hidden_dim,) * max(config.model.num_layers, 1),
            lr=config.optimizer.lr,
            device=config.device,
        ),
        config.data.task,
        config.trainer.epochs,
        batch_size=config.data.batch_size,
        device=config.device,
        seed=config.seed,
        batches_per_epoch=config.trainer.batches_per_epoch or None,
    )
    return final_metrics(history)
