"""The one path from "a learning rule and a task" to a trained system.

Five documented experiments and two public helpers used to reach training
through ``CoreTrainer``, which was removed in Sprint 7.6.10. Each grew its own
copy of the sequence -- build a config, construct a trainer, call ``fit``, then
read ``history[-1]`` with an attribute-access dance that could not work,
because ``fit`` has always returned a list of plain dicts.

This module is that sequence, once. It is deliberately narrow: a model
*factory* rather than a model *name*, because the zoo's names are the thing
that rotted, and a task *name* rather than a data pipeline, because that is
what the documented entry points have.
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

from computronium.core.system_trainer.config import SystemTrainerConfig
from computronium.core.system_trainer.trainer import SystemTrainer
from computronium.domains.factory import create_task

if TYPE_CHECKING:
    from collections.abc import Callable, Iterator

    from torch import Tensor
    from torch.utils.data import DataLoader

    from computronium.domains.trainer import TaskProtocol
    from computronium.ontology import System

__all__ = [
    "FlattenLoader",
    "TaskBatches",
    "final_metrics",
    "flat_input_dim",
    "train_on_task",
    "train_task",
]


def _flatten(inputs: Tensor, task: str) -> Tensor:
    """Flatten what an MLP geometry cannot consume: ``(B, C, H, W)`` and up.

    Non-float inputs are refused here rather than deep inside a geometry's
    energy computation. The language lane is the case that matters: it yields
    token *indices*, and there is no embedding geometry on the 5-D path, so
    the honest answer is which task cannot be trained, not which tensor
    multiply failed.
    """
    if not inputs.is_floating_point():
        raise ValueError(
            f"task {task!r} yields {inputs.dtype} inputs (token indices?), and an "
            "MLP geometry needs floats: the 5-D path has no embedding layer, so "
            "this task is not trainable through train_task()"
        )
    return inputs.reshape(inputs.size(0), -1) if inputs.dim() > 2 else inputs


class FlattenLoader:
    """A ``DataLoader`` wrapper that flattens inputs for MLP geometries."""

    def __init__(self, loader: DataLoader) -> None:
        self.loader = loader

    def __iter__(self) -> Iterator[tuple[Tensor, Tensor]]:
        for inputs, targets in self.loader:
            yield _flatten(inputs, "dataloader"), targets

    def __len__(self) -> int:
        return len(self.loader)


class TaskBatches:
    """One epoch of a task as ``(inputs, targets)`` pairs.

    Two lanes, because tasks do not agree on how a batch is produced. Most
    yield pairs from a ``DataLoader``; the language lane yields mapping
    batches and overrides ``get_batch`` instead. One peeked batch decides
    which lane a task is on, so a caller never has to know which kind of task
    it asked for, and a dataloader that does not fit is reported rather than
    silently mis-read.
    """

    def __init__(
        self,
        task: TaskProtocol,
        split: str,
        batch_size: int,
        batches_per_epoch: int | None,
    ) -> None:
        self.task = task
        self.split = split
        self.batch_size = batch_size
        self.batches_per_epoch = batches_per_epoch
        self._lane: str | None = None
        self._length = 0

    def _resolve(self) -> str:
        if self._lane is None:
            loader = self.task.get_dataloader(self.split)  # type: ignore[arg-type]
            first = next(iter(loader), None) if loader is not None else None
            self._lane = (
                "loader" if first is not None and _is_pair(first) else "get_batch"
            )
            if self._lane == "loader":
                self._length = len(loader)  # type: ignore[arg-type]
            elif self.batches_per_epoch is None:
                raise ValueError(
                    f"task {self.task.name!r} has no {self.split!r} dataloader "
                    "yielding (inputs, targets); pass batches_per_epoch to draw "
                    "that many batches through the task's own get_batch()"
                )
            else:
                self._length = self.batches_per_epoch
        return self._lane

    def __iter__(self) -> Iterator[tuple[Tensor, Tensor]]:
        if self._resolve() == "loader":
            loader = self.task.get_dataloader(self.split)  # type: ignore[arg-type]
            for inputs, targets in loader:  # type: ignore[union-attr]
                yield _flatten(inputs, self.task.name), targets
            return
        for _ in range(self.batches_per_epoch or 0):
            inputs, targets = self.task.get_batch(self.split, self.batch_size)
            yield _flatten(inputs, self.task.name), targets

    def __len__(self) -> int:
        self._resolve()
        return self._length


def _is_pair(batch: object) -> bool:
    """Is this batch an ``(inputs, targets)`` pair? Mapping batches are not."""
    return isinstance(batch, (tuple, list)) and len(batch) == 2


def flat_input_dim(input_dim: object, task: str) -> int:
    """The flattened input width, which is what an MLP geometry is sized by.

    Vision tasks report their unflattened shape (the registry's
    ``resolve_task`` makes the same reduction), so an MLP arm needs the
    product rather than the tuple.
    """
    if isinstance(input_dim, int):
        return input_dim
    if isinstance(input_dim, (tuple, list)) and all(
        isinstance(dim, int) for dim in input_dim
    ):
        return math.prod(input_dim)
    raise ValueError(
        f"task {task!r} reports input_dim={input_dim!r}, which is neither a width "
        "nor a shape, so no MLP geometry can be sized from it"
    )


def final_metrics(history: list[dict[str, float]]) -> dict[str, float]:
    """The last epoch's metrics, or ``{}`` for a run that trained nothing."""
    return history[-1] if history else {}


def train_task(
    model_factory: Callable[[int, int], System],
    task: str,
    epochs: int,
    *,
    batch_size: int = 64,
    device: str = "auto",
    quick_mode: bool = False,
    seed: int | None = None,
    batches_per_epoch: int | None = None,
) -> list[dict[str, float]]:
    """Train ``model_factory``'s system on the named ``task``.

    The named form, for callers that hold a task *name* (the documented
    ``python -m`` entry points). :func:`train_on_task` is the same path for
    callers that already hold a task object.

    Args:
        model_factory: Called with the task's ``(input_dim, output_dim)``; must
            return a composed :class:`~computronium.ontology.System`. The
            learning rate belongs to the system's update, not here.
        task: Task name understood by :func:`~computronium.domains.factory.create_task`.
        epochs: Epochs to train for.
        batch_size: Batch size for both the task's loaders and the trainer.
        device: ``"auto"``, ``"cpu"``, ``"cuda"`` or ``"mps"``.
        quick_mode: Ask the task for a reduced dataset.
        seed: Overrides the trainer's default seed when given.
        batches_per_epoch: Draw this many batches per epoch for tasks that
            have no ``(inputs, targets)`` dataloader (the language lane).

    Returns:
        One metrics dict per epoch, as :meth:`SystemTrainer.fit` produces it.
    """
    from computronium.utils import seed_everything

    if seed is not None:
        seed_everything(seed)
    handle = create_task(
        task, device=device, quick_mode=quick_mode, batch_size=batch_size
    )
    config = SystemTrainerConfig(
        max_epochs=epochs,
        batch_size=batch_size,
        val_batch_size=batch_size,
        device=device,
    )
    if seed is not None:
        config.seed = seed
    return train_on_task(
        model_factory, handle, config, batches_per_epoch=batches_per_epoch
    )


def train_on_task(
    model_factory: Callable[[int, int], System],
    task: TaskProtocol,
    config: SystemTrainerConfig,
    *,
    batches_per_epoch: int | None = None,
) -> list[dict[str, float]]:
    """Train ``model_factory``'s system on a task object the caller already has.

    Same path as :func:`train_task` minus task construction and the trainer
    config, for callers that hold a configured or folded task (k-fold
    validation, benchmarks) or a config with their own tracking flags, and
    would otherwise re-implement the loader wiring.

    Raises:
        ValueError: The task reports no usable input dimension or batch source.
            Both mean the task is not trainable through this path, and silently
            training on nothing would hide it.
    """
    task.setup()
    return SystemTrainer(
        system=model_factory(
            flat_input_dim(task.input_dim, task.name), task.output_dim
        ),
        config=config,
        train_data=TaskBatches(task, "train", config.batch_size, batches_per_epoch),
        val_data=TaskBatches(task, "val", config.batch_size, batches_per_epoch),
    ).fit()
