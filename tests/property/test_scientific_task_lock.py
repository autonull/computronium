"""Lock: the scientific domain is registered, measured, and classless (B7).

``ScientificTask`` was exported and constructible but absent from
``SUPPORTED_TASKS``, so coverage could not see the domain. Registering it
exposed a second defect: the pipeline computed class-match accuracy for every
target, and a ``[B, 3]`` float regression target crashed the validation pass
(``size of tensor a (32) must match tensor b (3)``). The accuracy rule now has
one source, ``core.losses.accuracy_tensor``, and a floating-point target
returns the declared 0.0 sentinel.

Each test fails if its mechanism is removed: the task name is deleted from the
registry, the row stops describing the loader, the sentinel becomes an argmax,
or the preregistration stops bracketing its ruler.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import torch

from computronium.core.losses import accuracy_tensor
from computronium.domains.base import DomainType, TaskSplit
from computronium.domains.factory import create_task
from computronium.domains.registry import SUPPORTED_TASKS, resolve_task
from computronium.domains.scientific import ScientificTask
from computronium.experiment.kernel.evaluate import _primary_domain_metric_key
from computronium.experiment.registry.task_registry import get_task_registry

_ROOT = Path(__file__).resolve().parents[2]
_REGISTRATION = _ROOT / "configs/preregistrations/b7_scientific_pendulum_state_mse.json"
_TASK = "pendulum_state"


def _loader() -> ScientificTask:
    task = ScientificTask(name=_TASK, dataset_name="pendulum", device="cpu")
    task.setup()
    return task


def _val_split() -> tuple[torch.Tensor, torch.Tensor]:
    loader = _loader().get_dataloader(TaskSplit.VAL)
    return (
        torch.cat([batch[0] for batch in loader]),
        torch.cat([batch[1] for batch in loader]),
    )


def test_scientific_task_is_supported_and_resolves() -> None:
    assert _TASK in SUPPORTED_TASKS
    assert type(create_task(_TASK, device="cpu", quick_mode=True)) is ScientificTask
    spec = resolve_task(_TASK)
    assert (spec.input_dim, spec.output_dim) == (3, 3)


def test_registry_row_matches_the_loader() -> None:
    task = _loader()
    row = get_task_registry().get(_TASK)
    assert row.domain is DomainType.SCIENTIFIC
    assert task.domain_type is DomainType.SCIENTIFIC
    assert row.input_shape == (task.input_dim,)
    assert row.output_dim == task.output_dim
    assert row.typical_batch_size == task.batch_size
    assert _primary_domain_metric_key(task.domain_type) == "mse"


def test_float_targets_report_the_regression_sentinel() -> None:
    logits = torch.randn(8, 3)
    target = torch.randn(8, 3)
    assert accuracy_tensor(logits, target).item() == 0.0
    # The classification rule is unchanged: class hits over labelled entries.
    classes = torch.tensor([0, 1, 2, 1])
    class_logits = torch.tensor([
        [9.0, 0.0, 0.0],
        [0.0, 9.0, 0.0],
        [0.0, 0.0, 9.0],
        [9.0, 0.0, 0.0],
    ])
    assert accuracy_tensor(class_logits, classes).item() == 0.75


def test_registration_brackets_its_ruler() -> None:
    payload = json.loads(_REGISTRATION.read_text())
    x, y = _val_split()
    per_sample = ((x - y) ** 2).mean(dim=1)
    identity = per_sample.mean().item()
    se = per_sample.std(unbiased=True).item() / math.sqrt(len(per_sample))

    assert payload["task"] == _TASK
    assert payload["metric"] == "val_loss"
    assert payload["ruler"]["value"] == round(identity, 5)
    assert payload["ruler"]["se"] == round(se, 5)
    assert (
        payload["ruler"]["value"]
        > payload["threshold"]
        > payload["noise_floor"]["value"]
    )
    assert payload["min_seeds"] >= 3
