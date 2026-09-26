"""``SystemTrainer``'s epoch record: what it measures, and what it admits.

``SystemTrainerConfig`` carried ``track_flops`` and ``track_memory`` as
configuration and nothing read them, so a caller that asked for a resource
budget got loss and accuracy and no resource numbers. These assert the
contract that replaced that: measured metrics are present, unmeasurable ones
are absent, and the per-epoch time budget flags the epoch it truncated.
"""

from __future__ import annotations

import pytest
import torch

from computronium.core.rules import rule_system
from computronium.core.system_trainer import SystemTrainer, SystemTrainerConfig


class _Batches:
    """A fixed list of ``(inputs, targets)`` pairs, re-iterable per epoch."""

    def __init__(self, n: int = 4, batch: int = 8, dim: int = 6, out: int = 3) -> None:
        self._pairs = [
            (torch.randn(batch, dim), torch.randint(0, out, (batch,))) for _ in range(n)
        ]

    def __iter__(self):
        return iter(self._pairs)

    def __len__(self) -> int:
        return len(self._pairs)


def _trainer(**config_kwargs: object) -> SystemTrainer:
    system = rule_system("ep", 6, 3, hidden_dims=(8,), device="cpu")
    return SystemTrainer(
        system=system,
        config=SystemTrainerConfig(max_epochs=1, device="cpu", **config_kwargs),  # type: ignore[arg-type]
        train_data=_Batches(),
    )


def test_an_epoch_is_timed_and_names_its_credit_route() -> None:
    trainer = _trainer()
    trainer.train_epoch()

    cost = trainer.epoch_resources[-1]
    assert cost.epoch_time_s > 0.0
    assert cost.budget_stopped is False
    assert sum(cost.training_paths.values()) == 4
    assert next(iter(cost.training_paths)) == "ThermodynamicContrast"


def test_resources_stay_out_of_the_reproducible_metrics_record() -> None:
    """A run's metrics must be bit-for-bit reproducible from its seed."""
    record = _trainer().train_epoch()

    for key in ("epoch_time_s", "peak_memory_mb", "forward_flops", "training_paths"):
        assert key not in record, f"{key!r} is machine state, not a model claim"


def test_flops_are_reported_when_the_config_asks_for_them() -> None:
    trainer = _trainer(track_flops=True)
    trainer.train_epoch()

    cost = trainer.epoch_resources[-1]
    assert cost.forward_flops is not None and cost.forward_flops > 0
    assert cost.backward_flops == 2 * cost.forward_flops


def test_flops_are_absent_when_the_config_declines_them() -> None:
    """An unmeasured metric is None, not zero -- the two are not the same."""
    trainer = _trainer(track_flops=False)
    trainer.train_epoch()

    cost = trainer.epoch_resources[-1]
    assert cost.forward_flops is None
    assert cost.backward_flops is None


def test_peak_memory_is_absent_on_a_cpu_run() -> None:
    """CUDA peak memory cannot be measured on CPU, so it is not reported."""
    trainer = _trainer(track_memory=True)
    trainer.train_epoch()

    assert trainer.epoch_resources[-1].peak_memory_mb is None


def test_a_time_budget_truncates_the_epoch_and_says_so() -> None:
    """A partial epoch's resources are not comparable, so it is flagged."""
    trainer = _trainer(max_epoch_time=1e-9)
    trainer.train_epoch()

    assert trainer.epoch_resources[-1].budget_stopped is True
    assert trainer.global_step == 1, "the budget must still count the batch it ran"


def test_no_budget_means_no_truncation() -> None:
    trainer = _trainer(max_epoch_time=0.0)
    trainer.train_epoch()

    assert trainer.global_step == 4


@pytest.mark.parametrize("epochs", [1, 2])
def test_fit_records_one_epoch_per_epoch(epochs: int) -> None:
    system = rule_system("ep", 6, 3, hidden_dims=(8,), device="cpu")
    history = SystemTrainer(
        system=system,
        config=SystemTrainerConfig(max_epochs=epochs, device="cpu"),
        train_data=_Batches(),
    ).fit()

    assert len(history) == epochs
