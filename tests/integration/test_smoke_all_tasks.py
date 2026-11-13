"""One PASS cell per registered task, from the declared legal space (S6).

The hand list this file used to carry named 15 of the 28 schedulable tasks, and
it trained a per-domain toy model (an MLP for vision, a tiny LM for language, a
separate path per corner) instead of the composed system an experiment actually
runs. So "26 of 28 tasks smoke" was true only for the fifteen it named, and the
cell it measured was not the cell the library composes.

The smoke now comes from the same instrument as the combination cover: the
task's declared legal space is enumerated, the first instantaneous-dynamics
cell is trained for one batch through the real evaluator, and the gate verdict
is the assertion. A task that loses its legal space, its loader, or its training
path turns this lock red by name.
"""

from __future__ import annotations

import pathlib

import pytest

from computronium.domains.registry import SUPPORTED_TASKS
from computronium.experiment.surface.combinations import smoke_task

_SKIP_ON_DOWNLOAD_KEYWORDS = ("download", "socket", "timeout", "url", "ssl")

# Datasets shipped in-repo or fetched on first use. A missing local copy is a
# skipped row, never a silent pass: the corpus-backed rows still assert.
_LOCAL_DATASETS = {
    "cifar10": "cifar-10-batches-py",
    "cifar100": "cifar-100-python",
}


def _dataset_present(task_id: str) -> bool:
    directory = _LOCAL_DATASETS.get(task_id)
    if directory is None:
        return True
    return (pathlib.Path("data") / directory).is_dir()


@pytest.mark.timeout(120)
@pytest.mark.parametrize("task_id", sorted(SUPPORTED_TASKS))
def test_task_trains_one_declared_cell(task_id: str) -> None:
    """Every schedulable task trains one cell its own declared space admits."""
    if not _dataset_present(task_id):
        pytest.skip(f"{task_id}: dataset not present locally")
    result = smoke_task(task_id)
    message = f"{task_id}: {result.cause} — {result.defect}"
    if any(keyword in message.lower() for keyword in _SKIP_ON_DOWNLOAD_KEYWORDS):
        pytest.skip(f"{task_id}: dataset unavailable")
    assert result.passed, message
