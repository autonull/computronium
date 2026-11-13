"""Lock: every task's loss is a declared inventory row (TODO91 S4).

A task's objective used to be whatever its ``compute_loss`` happened to
return, so a new task could add an untested loss and nothing noticed. The
inventory in ``core.losses`` declares the loss families; a task names one with
``loss_kind``. These tests fail when a task computes a loss its row does not
describe, when a continuous target is trained with cross-entropy, or when the
inventory loses a row.
"""

from __future__ import annotations

import math

import pytest
import torch
from torch import nn

from computronium.core.losses import LOSS_INVENTORY, LossKind
from computronium.domains.factory import create_task
from computronium.domains.registry import SUPPORTED_TASKS
from computronium.domains.trainer import _resolve_task_loss

# Offline loaders only: a network-shipped dataset would make this lock depend
# on the network, which is the defect S3 forbade.
OFFLINE_LOADERS = ("diabetes", "iris", "lorenz_state", "synthetic_forecast")

CLASS_LOGITS = torch.randn(8, 5, generator=torch.Generator().manual_seed(4))
CLASS_TARGETS = torch.tensor([0, 1, 2, 3, 4, 2, 1, 0])
VALUE_PREDS = torch.randn(8, 1, generator=torch.Generator().manual_seed(5))
VALUE_TARGETS = torch.randn(8, 1, generator=torch.Generator().manual_seed(6))


@pytest.fixture(scope="module")
def tasks():
    return {
        name: create_task(name, device="cpu", quick_mode=True)
        for name in SUPPORTED_TASKS
    }


def _canonical(kind: LossKind) -> tuple[torch.Tensor, torch.Tensor]:
    spec = LOSS_INVENTORY[kind]
    if spec.target == "class_index":
        return CLASS_LOGITS, CLASS_TARGETS
    return VALUE_PREDS, VALUE_TARGETS


def test_the_inventory_declares_every_loss_kind() -> None:
    assert set(LOSS_INVENTORY) == set(LossKind)
    for kind, spec in LOSS_INVENTORY.items():
        assert spec.kind is kind
        assert spec.metric_keys, kind
        assert spec.notes, kind


def test_the_inventory_rows_are_not_the_same_rule() -> None:
    """Each row's baseline predictor scores its declared ruler, not another's."""
    ce, mse = (
        LOSS_INVENTORY[LossKind.CROSS_ENTROPY],
        LOSS_INVENTORY[LossKind.MEAN_SQUARED_ERROR],
    )
    assert ce.target != mse.target
    assert ce.metric_keys != mse.metric_keys

    # A uniform class predictor scores ln(C); a zero-value predictor scores
    # the target's mean square. These are the two rulers the rows declare.
    uniform = torch.zeros(4, 5)
    assert math.isclose(
        float(ce.fn(uniform, torch.zeros(4, dtype=torch.long))),
        math.log(5),
        rel_tol=1e-6,
    )
    assert float(mse.fn(torch.zeros(4, 1), torch.full((4, 1), 2.0))) == 4.0


def test_every_task_declares_an_inventory_loss(tasks) -> None:
    missing = [
        name for name, task in tasks.items() if task.loss_kind not in LOSS_INVENTORY
    ]
    assert not missing, missing


def test_every_task_computes_its_declared_loss(tasks) -> None:
    for name, task in tasks.items():
        spec = LOSS_INVENTORY[task.loss_kind]
        logits, targets = _canonical(task.loss_kind)
        computed = task.compute_loss(logits, targets)
        assert torch.equal(computed, spec.fn(logits, targets)), (
            f"{name}: compute_loss is not the declared {task.loss_kind} row"
        )


def test_the_training_lane_loss_follows_the_declared_row(tasks) -> None:
    """``_resolve_task_loss`` reads ``loss_kind``, not the domain name."""
    for name, task in tasks.items():
        spec = LOSS_INVENTORY[task.loss_kind]
        resolved = _resolve_task_loss(task)
        expected = nn.MSELoss if spec.target == "continuous" else nn.CrossEntropyLoss
        assert isinstance(resolved, expected), (
            f"{name}: lane loss {type(resolved).__name__} contradicts the "
            f"{task.loss_kind} row"
        )


@pytest.mark.parametrize("name", OFFLINE_LOADERS)
def test_target_dtype_matches_the_declared_row(name: str) -> None:
    """A batch whose target is a value must be declared continuous, and back."""
    task = create_task(name, device="cpu", quick_mode=True)
    _inputs, targets = task.get_batch("train")
    spec = LOSS_INVENTORY[task.loss_kind]
    assert targets.is_floating_point() == (spec.target == "continuous"), name
