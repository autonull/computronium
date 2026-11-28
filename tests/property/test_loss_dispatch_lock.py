"""Lock: the task-loss dispatch, both directions (TODO108 W49).

``_compute_task_loss`` enters the ``_CustomLoss`` protocol when a task defines
``compute_loss`` and otherwise resolves the declared ``loss_kind``. Both
directions are asserted with stub tasks, so a branch that silently takes the
other path fails.
"""

from __future__ import annotations

import torch
from torch import nn

from computronium.core.losses import LossKind
from computronium.domains.trainer import _compute_task_loss


class _StubTask:
    """A task that only declares its loss kind (the no-custom branch)."""

    loss_kind = LossKind.CROSS_ENTROPY


class _RegressionStubTask(_StubTask):
    loss_kind = LossKind.MEAN_SQUARED_ERROR


class _CustomLossStubTask(_StubTask):
    """A task that computes its own loss (the LM/regression reshape branch)."""

    def compute_loss(self, logits: torch.Tensor, targets: torch.Tensor) -> torch.Tensor:
        return torch.full((), 7.0, dtype=logits.dtype)


def test_custom_compute_loss_is_used_when_declared() -> None:
    task = _CustomLossStubTask()
    logits = torch.zeros(2, 3)
    targets = torch.zeros(2, dtype=torch.long)

    loss = _compute_task_loss(task, logits, targets)

    assert loss.item() == 7.0


def test_cross_entropy_is_resolved_when_no_custom_loss() -> None:
    task = _StubTask()
    logits = torch.tensor([[2.0, 0.0], [0.0, 2.0]])
    targets = torch.tensor([0, 1])

    loss = _compute_task_loss(task, logits, targets)

    expected = nn.functional.cross_entropy(logits, targets)
    torch.testing.assert_close(loss, expected)


def test_mean_squared_error_is_resolved_for_a_continuous_target() -> None:
    task = _RegressionStubTask()
    logits = torch.tensor([[0.5], [1.5]])
    targets = torch.tensor([[0.0], [1.0]])

    loss = _compute_task_loss(task, logits, targets)

    expected = nn.functional.mse_loss(logits, targets)
    torch.testing.assert_close(loss, expected)
