"""Lock: the task surface is constructible, and a regression row is not a class row (S3).

``SUPPORTED_TASKS`` is the schedulable set, so a name in it must construct
without touching the network. The offline loaders added by S3 — ``diabetes``
(tabular regression) and ``lorenz_state`` (scientific ODE) — must also
describe themselves honestly: a continuous target has no class rate, and its
MSE is read in target-variance units so 1.0 means the train-mean predictor.

Each test fails if its mechanism is removed: a name leaves the registry, the
regression branch falls back to cross-entropy, or the target stops being
standardized.
"""

from __future__ import annotations

import torch
from torch import nn

from computronium.domains.base import DomainType, TaskSplit
from computronium.domains.factory import create_task
from computronium.domains.registry import SUPPORTED_TASKS, resolve_task
from computronium.domains.tabular import TabularTask
from computronium.domains.trainer import _resolve_task_loss
from computronium.experiment.kernel.evaluate import _primary_domain_metric_key
from computronium.experiment.registry.task_registry import get_task_registry

OFFLINE_LOADERS = ("diabetes", "lorenz_state")


def test_every_supported_task_constructs_offline() -> None:
    """A schedulable name must resolve to a task object without a download."""
    for name in sorted(SUPPORTED_TASKS):
        task = create_task(name, device="cpu", quick_mode=True)
        assert task is not None, name
        assert task.domain_type is not DomainType.UNKNOWN, name


def test_continual_task_ids_are_declared() -> None:
    """A continual task is creatable from its bare id (TODO104 A14).

    ``SplitMNIST`` raises on first use when no split is set, so a bare
    ``split_mnist`` id must carry its declared default split; removing it
    makes the registry row unusable and every cell on that family a defect.
    """
    task = create_task("split_mnist", device="cpu", quick_mode=True)
    assert getattr(task, "task_id", None) is not None


def test_offline_names_are_supported_and_resolve() -> None:
    expected = {"diabetes": (10, 1), "lorenz_state": (3, 3)}
    for name, shape in expected.items():
        assert name in SUPPORTED_TASKS
        spec = resolve_task(name)
        assert (spec.input_dim, spec.output_dim) == shape, name


def test_registry_rows_match_their_loaders() -> None:
    for name in OFFLINE_LOADERS:
        task = create_task(name, device="cpu", quick_mode=True)
        task.setup()
        row = get_task_registry().get(name)
        assert row.domain is task.domain_type, name
        assert row.input_shape == (task.input_dim,), name
        assert row.output_dim == task.output_dim, name
        assert row.typical_batch_size == task.batch_size, name
        assert _primary_domain_metric_key(task.domain_type) == (
            "accuracy" if row.domain is DomainType.TABULAR else "mse"
        )


def test_diabetes_is_regression_with_a_declared_ruler() -> None:
    task = create_task("diabetes", device="cpu", quick_mode=True)
    assert type(task) is TabularTask
    task.setup()

    row = get_task_registry().get("diabetes")
    assert next(obj.payload_key for obj in row.measured_objectives()) == "val_loss"

    _inputs, targets = task.get_batch(TaskSplit.TRAIN)
    assert targets.is_floating_point(), "a regression target is a value, not an index"
    assert targets.shape[-1] == 1

    # Standardized by the training split's own statistics, so the zero
    # predictor scores ~1.0 and every MSE is read against that ruler.
    zero = torch.zeros_like(targets)
    assert 0.5 < float(task.compute_loss(zero, targets)) < 2.0

    metrics = task.evaluate(nn.Linear(task.input_dim, task.output_dim))
    assert "accuracy" not in metrics.to_dict()
    assert "mse" in metrics.to_dict()


def test_regression_lane_resolves_mse_not_cross_entropy() -> None:
    task = create_task("diabetes", device="cpu", quick_mode=True)
    assert isinstance(_resolve_task_loss(task), nn.MSELoss)


def test_train_statistics_define_the_regression_ruler() -> None:
    """Standardization is fitted on the training split, which is the ruler."""
    task = create_task("diabetes", device="cpu", quick_mode=True)
    task.setup()
    train_idx, val_idx = task.fold_indices(5)[0]
    train_targets = task._y[train_idx]
    val_targets = task._y[val_idx]
    assert abs(float(train_targets.mean())) < 0.1
    assert abs(float(train_targets.std()) - 1.0) < 0.1
    # Held-out rows are standardized by the same statistics, so their scale is
    # comparable but not forced to 1: the metric is not fitted to itself.
    assert 0.5 < float(val_targets.std()) < 2.0


def test_an_unemitted_objective_carries_its_reason() -> None:
    """A declared-but-unmeasured objective names what would emit it."""
    registry = get_task_registry()
    silent = [
        (task.name, obj.name)
        for task in registry
        for obj in task.objectives
        if not obj.is_measured and not obj.unavailable_reason and obj.payload_key
    ]
    assert not silent, silent
    reasons = {
        obj.name: obj.unavailable_reason
        for task in registry
        for obj in task.unmeasured_objectives()
    }
    for name in ("forgetting", "backward_transfer"):
        assert reasons.get(name), name
