"""``train_task`` is the one path from a learning rule and a task to a run.

Covers the three things the documented entry points depend on and that no
other test exercised while they were unimportable: the two batch lanes
(dataloader and ``get_batch``), the input-width reduction a vision task needs,
and the refusals for tasks that cannot be trained this way at all.
"""

from __future__ import annotations

import pytest

from computronium.core.rules import RULES, rule_for, rule_system
from computronium.core.system_trainer.factory import param_count
from computronium.core.system_trainer.train_task import (
    TaskBatches,
    final_metrics,
    train_task,
)


def _factory(rule: str = "backprop", width: int = 16):
    def build(input_dim: int, output_dim: int):
        return rule_system(
            rule, input_dim, output_dim, hidden_dims=(width,), device="cpu"
        )

    return build


def test_trains_a_task_and_reports_epoch_metrics() -> None:
    history = train_task(
        _factory(), "xor", 2, batch_size=32, device="cpu", quick_mode=True
    )

    assert len(history) == 2
    assert {"epoch", "train_loss", "train_acc", "val_acc", "val_loss"} <= set(
        history[-1]
    )
    assert final_metrics(history) == history[-1]


def test_reduces_a_vision_task_to_its_flattened_width() -> None:
    widths: list[int] = []

    def build(input_dim: int, output_dim: int):
        widths.append(input_dim)
        return rule_system(
            "backprop", input_dim, output_dim, hidden_dims=(8,), device="cpu"
        )

    train_task(build, "xor", 1, batch_size=16, device="cpu", quick_mode=True)

    assert widths == [2], "the factory must be sized by the flattened input"


def test_final_metrics_is_empty_for_a_run_that_trained_nothing() -> None:
    assert final_metrics([]) == {}


class _NoBatchTask:
    """A task with neither a dataloader nor a stated epoch length."""

    name = "no_batches"
    input_dim = 4
    output_dim = 2
    device = "cpu"
    quick_mode = False

    def setup(self) -> None:
        return None

    def get_dataloader(self, split: str) -> None:
        return None

    def get_batch(self, split: str, batch_size: int) -> tuple:  # pragma: no cover
        raise AssertionError("the epoch length must be demanded first")


def test_a_task_without_batches_is_refused_with_the_way_out() -> None:
    batches = TaskBatches(_NoBatchTask(), "train", 8, None)  # type: ignore[arg-type]

    with pytest.raises(ValueError, match="batches_per_epoch"):
        list(batches)


@pytest.mark.parametrize("rule", RULES)
def test_every_named_rule_builds_a_system(rule: str) -> None:
    system = rule_system(rule, 6, 3, hidden_dims=(8,), device="cpu")

    assert param_count(system) > 0


def test_an_unknown_rule_name_is_refused_with_the_known_ones() -> None:
    with pytest.raises(KeyError, match="known rules"):
        rule_system("not-a-rule", 6, 3, hidden_dims=(8,), device="cpu")


def test_zoo_model_names_name_a_rule() -> None:
    assert rule_for("eqprop_mlp") == "ep"
    assert rule_for("backprop_mlp") == "backprop"
    with pytest.raises(KeyError, match="known"):
        rule_for("no_such_model")
