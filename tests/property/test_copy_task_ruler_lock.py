"""Lock: the copy task's rulers, and the ceiling its framing puts above them (B6b).

``copy_task`` carries ``y = seq[t]`` in the input vector at index ``t``, and ``t``
is recoverable from the pad count, so a positional copy reads every target: the
copy-the-input baseline is the task's ceiling (1.000), not a number an arm can
beat. The claim therefore registers the *fixed-policy* rulers — policies that
use no addressing — and reports the ceiling as the bound. These tests keep the
three facts apart, so a task repair that removes the leak fails here and the
preregistration must be re-derived.

They also lock the registry row to the loader — the row declared ``(10,)``/``2``
while the loader emits ``(21,)``/``8`` — and the task class to the domain it is
registered under.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import pytest
import torch

from computronium.domains.base import DomainType, TaskSplit
from computronium.domains.factory import CopyTask
from computronium.experiment.registry.task_registry import get_task_registry

#: A fixed policy lands within this of the vocabulary-uniform rate. 2,000 quick
#: rows give SE 0.0074, so this is ~6.8 SE — wide enough for a resampled split.
CHANCE_TOLERANCE = 0.05

#: The claim's rulers are registered, so the lock reads the threshold it locks.
PREREGISTRATION = (
    Path(__file__).resolve().parents[2]
    / "configs/preregistrations/b6b_memory_copy_task_token_accuracy.json"
)


@pytest.fixture(scope="module")
def copy_split() -> tuple[torch.Tensor, torch.Tensor, CopyTask]:
    torch.manual_seed(0)
    task = CopyTask(device="cpu", quick_mode=True)
    task.setup()
    batches = list(task.get_dataloader(TaskSplit.VAL))
    inputs, targets = (torch.cat(part) for part in zip(*batches, strict=True))
    return inputs, targets, task


def _step_index(inputs: torch.Tensor, task: CopyTask) -> torch.Tensor:
    """The sample's own copy step, read the way a positional policy reads it."""
    pad = task.vocab_size + 1
    return (inputs != pad).sum(dim=1) - (task.seq_len + 1)


def _accuracy(prediction: torch.Tensor, targets: torch.Tensor) -> float:
    return float((prediction == targets).double().mean())


def _policies(
    inputs: torch.Tensor, targets: torch.Tensor, task: CopyTask
) -> dict[str, torch.Tensor]:
    """The pinned policies: fixed-policy rulers, the stepping leak, the ceiling."""
    steps = _step_index(inputs, task)
    rows = torch.arange(len(targets))
    return {
        "all_zero": torch.zeros_like(targets),
        "copy_one_step": torch.where(
            steps > 0,
            inputs[rows, (steps - 1).clamp(min=0)].long(),
            torch.zeros_like(targets),
        ),
        "majority_token": torch.full_like(targets, int(targets.mode().values)),
        "positional_copy": inputs[rows, steps].long(),
    }


def test_copy_the_input_ceiling_reads_every_target(copy_split) -> None:
    """The answer sits at index ``t``; a positional copy scores exactly 1.000."""
    inputs, targets, task = copy_split
    steps = _step_index(inputs, task)
    assert int(steps.min()) == 0
    assert int(steps.max()) == task.seq_len - 1
    positional = _policies(inputs, targets, task)["positional_copy"]
    assert _accuracy(positional, targets) == 1.0


def test_fixed_policy_rulers_sit_at_chance(copy_split) -> None:
    """Policies that address nothing land on the vocabulary-uniform rate."""
    inputs, targets, task = copy_split
    chance = 1.0 / task.vocab_size
    policies = _policies(inputs, targets, task)
    for name, prediction in policies.items():
        if name == "positional_copy":
            continue
        assert abs(_accuracy(prediction, targets) - chance) < CHANCE_TOLERANCE, name


def test_registry_row_matches_the_loader(copy_split) -> None:
    """A stale row hides the task's real shape from the search space."""
    inputs, targets, task = copy_split
    spec = get_task_registry().get(task.name)
    assert spec.input_shape == (inputs.shape[1],)
    assert spec.output_dim == int(targets.max()) + 1
    # The row declares the schedule's batch size, not the quick-mode one, so the
    # comparison is against the task's own single source rather than a literal.
    assert CopyTask(device="cpu")._batch_size == spec.typical_batch_size


def test_copy_task_declares_the_domain_it_is_registered_under(copy_split) -> None:
    """One source of truth: the task class and the registry row agree."""
    _, _, task = copy_split
    assert task.domain_type is DomainType.MEMORY
    assert task.spec.domain_type is DomainType.MEMORY
    assert get_task_registry().get(task.name).domain is DomainType.MEMORY


def test_the_registration_brackets_rulers_and_ceiling(copy_split) -> None:
    """The registered threshold sits above every fixed ruler, below the ceiling."""
    inputs, targets, task = copy_split
    policies = _policies(inputs, targets, task)
    ceiling = _accuracy(policies["positional_copy"], targets)
    rulers = [
        _accuracy(prediction, targets)
        for name, prediction in policies.items()
        if name != "positional_copy"
    ]
    registration = json.loads(PREREGISTRATION.read_text())
    threshold = registration["threshold"]
    assert max(rulers) < threshold < ceiling
    assert math.isclose(registration["ceiling"]["value"], ceiling, abs_tol=1e-9)
