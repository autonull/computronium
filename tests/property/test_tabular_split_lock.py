"""Lock: a tabular task holds out every class, and says its majority rate (N1).

``TabularTask`` split by slicing ``X[:n]`` / ``X[n:]``. sklearn ships iris and
wine ordered by class, so wine's 36-row validation set was entirely class 2
while the train set held only 12 class-2 rows: every arm read ``val_acc=0.0``
(train 0.88-0.90) and looked like a broken credit rule. The split is now
stratified and deterministic, and the evaluation reports the majority-class
rate beside accuracy so a chance-level cell reads as chance.

Falsified by reverting the slice: wine's validation set holds one class and the
majority baseline is 1.0.
"""

from __future__ import annotations

import torch

from computronium.domains.base import TaskSplit
from computronium.domains.tabular import TabularTask


def _labels(task: TabularTask, split: TaskSplit) -> torch.Tensor:
    return torch.cat([targets for _, targets in task.get_dataloader(split)])


def _task(dataset: str) -> TabularTask:
    return TabularTask(name=dataset, dataset_name=dataset, device="cpu")


def test_every_class_survives_the_split() -> None:
    """Both splits of wine and iris carry all three classes."""
    for dataset in ("wine", "iris"):
        task = _task(dataset)
        task.setup()
        train_classes = set(_labels(task, TaskSplit.TRAIN).tolist())
        val_classes = set(_labels(task, TaskSplit.VAL).tolist())
        assert train_classes == {0, 1, 2}, dataset
        assert val_classes == {0, 1, 2}, dataset


def test_val_split_is_not_single_class() -> None:
    """The defect's exact shape: a validation split with one class."""
    task = _task("wine")
    task.setup()
    val = _labels(task, TaskSplit.VAL)
    counts = val.bincount()
    assert counts.numel() == 3
    assert counts.min() >= 10  # 12 per class at test_size=0.2 of 178 rows
    assert counts.max().item() / val.numel() < 0.5


def test_evaluate_reports_majority_baseline() -> None:
    """A cell reports the rate a constant predictor reaches on this split."""
    task = _task("wine")
    task.setup()
    model = torch.nn.Linear(task.input_dim, 3)
    metrics = task.evaluate(model, split=TaskSplit.VAL)

    val = _labels(task, TaskSplit.VAL)
    expected = val.bincount().max().item() / val.numel()
    assert metrics.custom["majority_baseline"] == expected
    assert metrics.custom["val_acc_over_majority"] == metrics.accuracy - expected
    assert metrics.to_dict()["majority_baseline"] == expected


def test_folds_partition_every_row_and_select_one() -> None:
    """The fold path is a real partition, not a second holdout (T2).

    Five stratified folds must cover every row exactly once, keep all three
    classes in every validation fold, and ``set_fold`` must install that fold's
    loaders. Falsified by returning overlapping folds or by ignoring the fold
    index: the validation size would not be 30 or the coverage would not be 1.
    """
    task = _task("iris")
    task.setup()
    folds = task.fold_indices(5)
    seen = torch.zeros(len(task._X), dtype=torch.int)
    for train_idx, val_idx in folds:
        assert not set(train_idx) & set(val_idx)
        seen[torch.as_tensor(val_idx)] += 1
        assert set(task._y[val_idx].tolist()) == {0, 1, 2}
    assert bool((seen == 1).all())

    task.set_fold(2, 5)
    assert len(_labels(task, TaskSplit.VAL)) == len(folds[2][1]) == 30
