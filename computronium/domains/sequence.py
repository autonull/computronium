"""Time-major sequence tasks (TODO93 §19 — the temporal axis's task family).

Every other loader yields 2-D batches ``(batch, features)``; a temporal credit
reads ``x (time, batch, input)`` and ``y (time, batch)``, so it had no task
outside its own fixture. ``SequenceTask`` owns that contract end-to-end: the
dataset stores one ``(time, input)``/``(time,)`` item and ``SequenceBatches``
moves the time axis first. The composer gives the geometry its time axis from
the credit that reads it (``requires_sequence``), so the loader and the
geometry cannot disagree about the layout.

The family is a **delayed cue**: a one-hot class at ``cue_step``, noise at
every other step, and the class as the label at *every* step. Reading the cue
at its own step cannot beat chance on the other steps — the hidden state has
to carry it forward — so the task has a real chance floor (``1/classes``)
and a memory requirement rather than a shortcut.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import torch
from torch import nn
from torch.utils.data import DataLoader, Dataset

from computronium.core.losses import accuracy_tensor, fold_time
from computronium.domains.base import (
    DomainSpec,
    DomainTask,
    DomainType,
    Metrics,
    TaskSplit,
)

if TYPE_CHECKING:
    from collections.abc import Iterator

__all__ = [
    "SequenceBatches",
    "SequenceTask",
]

_NOISE = 0.1


class _DelayedCueDataset(Dataset):
    """One item is ``x (time, input)`` with one cue step and ``y (time,)``."""

    def __init__(
        self,
        size: int,
        *,
        time: int,
        input_dim: int,
        classes: int,
        cue_step: int,
        seed: int,
    ) -> None:
        generator = torch.Generator().manual_seed(seed)
        labels = torch.randint(0, classes, (size,), generator=generator)
        x = torch.randn((size, time, input_dim), generator=generator) * _NOISE
        rows = torch.arange(size)
        x[rows, cue_step, :] = 0.0
        x[rows, cue_step, labels] = 1.0
        y = labels.unsqueeze(1).expand(size, time).contiguous()
        self._x = x
        self._y = y

    def __len__(self) -> int:
        return self._x.shape[0]

    def __getitem__(self, index: int) -> tuple[torch.Tensor, torch.Tensor]:
        return self._x[index], self._y[index]


class SequenceBatches:
    """A loader view that yields the time axis first.

    ``DataLoader`` batches an item's ``(time, input)`` to ``(batch, time,
    input)``; the temporal contract is the transpose, so this one class is
    the single place the layout is fixed (a second transpose elsewhere would
    disagree with it).
    """

    def __init__(
        self,
        dataset: Dataset,
        *,
        batch_size: int,
        shuffle: bool,
        seed: int = 0,
        num_workers: int = 0,
    ) -> None:
        self._loader = DataLoader(
            dataset,
            batch_size=batch_size,
            shuffle=shuffle,
            generator=torch.Generator().manual_seed(seed) if shuffle else None,
            num_workers=num_workers,
        )

    def __iter__(self) -> Iterator[tuple[torch.Tensor, torch.Tensor]]:
        for x, y in self._loader:
            yield x.transpose(0, 1), y.transpose(0, 1)

    def __len__(self) -> int:
        return len(self._loader)


class SequenceTask(DomainTask):
    """A synthetic delayed-cue sequence task (rung-1 fixture for the time axis)."""

    def __init__(  # ruff: ignore[too-many-arguments, too-many-positional-arguments]
        self,
        name: str = "delayed_cue",
        device: str = "cpu",
        quick_mode: bool = False,
        time: int = 12,
        cue_step: int = 2,
        classes: int = 10,
        n_train: int = 1024,
        n_val: int = 512,
        batch_size: int = 64,
        num_workers: int = 0,
        **kwargs,
    ):
        super().__init__(
            name,
            device=device,
            batch_size=batch_size,
            quick_mode=quick_mode,
            **kwargs,
        )
        self.time = time
        self.cue_step = cue_step
        self.classes = classes
        self.n_train = 256 if quick_mode else n_train
        self.n_val = 128 if quick_mode else n_val
        self.num_workers = num_workers
        self._train_batches: SequenceBatches | None = None
        self._val_batches: SequenceBatches | None = None
        self._input_dim = classes
        self._output_dim = classes

    @property
    def domain_type(self) -> DomainType:
        return DomainType.MEMORY

    @property
    def spec(self) -> DomainSpec:
        return DomainSpec(
            name=self.name,
            domain_type=DomainType.MEMORY,
            description=(
                "Delayed cue over a noisy stream: a one-hot class at "
                f"step {self.cue_step} of {self.time}, labelled at every step"
            ),
            default_metrics=["accuracy", "loss"],
            typical_input_shape=(self.classes,),
            typical_output_shape=(self.classes,),
            supported_tasks=["sequence_classification"],
            default_batch_size=64,
            default_lr=1e-2,
            requires_sequence=True,
            tags=["sequence", "memory", "temporal"],
        )

    def setup(self) -> None:
        train_ds = _DelayedCueDataset(
            self.n_train,
            time=self.time,
            input_dim=self.classes,
            classes=self.classes,
            cue_step=self.cue_step,
            seed=0,
        )
        val_ds = _DelayedCueDataset(
            self.n_val,
            time=self.time,
            input_dim=self.classes,
            classes=self.classes,
            cue_step=self.cue_step,
            seed=1,
        )
        self._train_batches = SequenceBatches(
            train_ds,
            batch_size=self.batch_size,
            shuffle=True,
            seed=0,
            num_workers=self.num_workers,
        )
        self._val_batches = SequenceBatches(
            val_ds,
            batch_size=self.batch_size,
            shuffle=False,
            num_workers=self.num_workers,
        )
        self._setup_done = True

    def get_dataloader(self, split: TaskSplit) -> SequenceBatches:
        if not self._setup_done:
            self.setup()
        loader = self._train_batches if split is TaskSplit.TRAIN else self._val_batches
        if loader is None:
            raise TypeError("SequenceTask.get_dataloader reads a set-up task")
        return loader

    def evaluate(
        self,
        model: nn.Module,
        split: TaskSplit = TaskSplit.VAL,
        max_batches: int | None = None,
    ) -> Metrics:
        was_training = model.training
        model.eval()
        loader = self.get_dataloader(split)
        total_loss = 0.0
        total_correct = 0.0
        total_rows = 0
        try:
            with torch.no_grad():
                for index, (batch_x, batch_y) in enumerate(loader):
                    if max_batches and index >= max_batches:
                        break
                    x = batch_x.to(self.device)
                    y = batch_y.to(self.device)
                    logits, y = fold_time(model(x), y)
                    rows = logits.shape[0]
                    total_loss += self.compute_loss(logits, y).item() * rows
                    total_correct += accuracy_tensor(logits, y).item() * rows
                    total_rows += rows
        finally:
            if was_training:
                model.train()
        denom = max(total_rows, 1)
        return Metrics(loss=total_loss / denom, accuracy=total_correct / denom)
