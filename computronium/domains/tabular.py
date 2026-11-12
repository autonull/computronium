"""
Tabular Domain Tasks

Standard tabular/structured data datasets.
"""

import numpy as np
import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset

from computronium.domains.base import (
    DomainSpec,
    DomainTask,
    DomainType,
    Metrics,
    TaskSplit,
)

__all__ = [
    "TabularTask",
]


class TabularTask(DomainTask):
    """Tabular/structured data domain tasks."""

    def __init__(
        self,
        name: str = "digits",
        dataset_name: str = "digits",
        **kwargs,
    ):
        super().__init__(name, **kwargs)
        self.dataset_name = dataset_name

    @property
    def domain_type(self) -> DomainType:
        return DomainType.TABULAR

    @property
    def spec(self) -> DomainSpec:
        return DomainSpec(
            name=self.name,
            domain_type=DomainType.TABULAR,
            description=f"Tabular task: {self.dataset_name}",
            default_metrics=["accuracy", "loss"],
            supported_tasks=["classification", "regression"],
            default_batch_size=32,
            default_lr=1e-3,
            tags=["tabular", "structured-data"],
        )

    def setup(self) -> None:
        if self._setup_done:
            return
        from sklearn.datasets import (
            load_breast_cancer,
            load_digits,
            load_iris,
            load_wine,
        )

        _DATASETS = {  # ruff: ignore[used-dummy-variable]
            "digits": load_digits,
            "breast_cancer": load_breast_cancer,
            "wine": load_wine,
            "iris": load_iris,
        }

        if self.dataset_name not in _DATASETS:
            raise ValueError(
                f"Unknown tabular dataset: {self.dataset_name}. "
                f"Available: {list(_DATASETS.keys())}"
            )

        data = _DATASETS[self.dataset_name]()
        X = data.data.astype(np.float32)
        y = data.target.astype(np.int64)

        # Normalize
        X = (X - X.mean(axis=0)) / (X.std(axis=0) + 1e-8)

        self._X = X
        self._y = y
        self._fold: int | None = None
        self._n_folds = 0

        # Stratified, deterministic split. sklearn ships iris/wine ordered by
        # class, so the tail slice held out ONE class — wine's validation was
        # 36 class-2 rows against a train set of 12, and every arm read 0.0.
        from sklearn.model_selection import train_test_split

        train_idx, val_idx = train_test_split(
            np.arange(X.shape[0]), test_size=0.2, random_state=0, stratify=y
        )
        self._set_loaders(np.asarray(train_idx), np.asarray(val_idx))

        self._input_dim = X.shape[1]
        self._output_dim = len(data.target_names)
        self._setup_done = True

    def _set_loaders(self, train_idx: np.ndarray, val_idx: np.ndarray) -> None:
        X_train = torch.from_numpy(self._X[train_idx])
        y_train = torch.from_numpy(self._y[train_idx])
        X_val = torch.from_numpy(self._X[val_idx])
        y_val = torch.from_numpy(self._y[val_idx])
        self._train_loader = DataLoader(
            TensorDataset(X_train, y_train), batch_size=self.batch_size, shuffle=True
        )
        self._val_loader = DataLoader(
            TensorDataset(X_val, y_val), batch_size=self.batch_size, shuffle=False
        )
        self._test_loader = self._val_loader

    def fold_indices(self, n_folds: int = 5) -> list[tuple[np.ndarray, np.ndarray]]:
        """Deterministic stratified folds, shared with any reference comparison.

        The same indices must drive every arm compared on a fold-mean, so this
        method is the single source of the split. ``random_state=0`` and
        ``shuffle=True`` make it reproducible across processes.

        Returns:
            One ``(train_indices, val_indices)`` pair per fold.
        """
        if not self._setup_done:
            self.setup()
        from sklearn.model_selection import StratifiedKFold

        splitter = StratifiedKFold(n_splits=n_folds, shuffle=True, random_state=0)
        return list(splitter.split(self._X, self._y))

    def set_fold(self, fold: int, n_folds: int) -> None:
        """Select one stratified fold as validation; the rest becomes training.

        ``cross_validate`` calls this before each fold's ``train_on_task``. A
        validation split of 30 rows resolves to 0.033 per sample, so a claim
        below one row's resolution is not readable from a single holdout.
        """
        if n_folds < 2 or not 0 <= fold < n_folds:
            raise ValueError(f"fold {fold} out of range for {n_folds} folds")
        folds = self.fold_indices(n_folds)
        self._fold = fold
        self._n_folds = n_folds
        train_idx, val_idx = folds[fold]
        self._set_loaders(np.asarray(train_idx), np.asarray(val_idx))

    def get_dataloader(self, split: TaskSplit) -> DataLoader:
        if not self._setup_done:
            self.setup()

        loader = self._train_loader if split == TaskSplit.TRAIN else self._val_loader
        if loader is None:
            raise RuntimeError("TabularTask loaders are not built")
        return loader

    def evaluate(
        self,
        model: nn.Module,
        split: TaskSplit = TaskSplit.VAL,
        max_batches: int | None = None,
    ) -> Metrics:
        model.eval()
        loader = self.get_dataloader(split)

        total_loss = 0.0
        total_correct = 0
        total_samples = 0
        labels: list[torch.Tensor] = []

        with torch.no_grad():
            for i, (inputs, targets) in enumerate(loader):
                if max_batches and i >= max_batches:
                    break

                inputs, targets = inputs.to(self.device), targets.to(self.device)  # ruff: ignore[redefined-loop-name]
                outputs = model(inputs)
                loss = self.compute_loss(outputs, targets)

                total_loss += loss.item() * inputs.size(0)
                total_correct += (outputs.argmax(1) == targets).sum().item()
                total_samples += inputs.size(0)
                labels.append(targets.detach().cpu().view(-1))

        avg_loss = total_loss / total_samples if total_samples > 0 else 0.0
        accuracy = total_correct / total_samples if total_samples > 0 else 0.0

        # A small held-out split is unreadable alone: report the majority-class
        # rate beside accuracy so a cell at chance is visibly at chance.
        majority_baseline = 0.0
        if labels:
            y_all = torch.cat(labels)
            if y_all.numel():
                majority_baseline = y_all.bincount().max().item() / y_all.numel()

        return Metrics(
            loss=avg_loss,
            accuracy=accuracy,
            custom={
                "majority_baseline": majority_baseline,
                "val_acc_over_majority": accuracy - majority_baseline,
            },
        )
