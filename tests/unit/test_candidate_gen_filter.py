"""``CandidateGenerator`` must resolve the task groups it filters on.

``_matches_filter`` branched on ``TASK_GROUPS`` without importing it, so any
non-``"all"`` task filter raised ``NameError`` — the CLI's ``--task-filter``
path, which no test reached.
"""

from pathlib import Path

import pytest

from computronium.execution._state import ExperimentState
from computronium.execution.candidate_gen import (
    CandidateGenerator,
    ExecutionStrategyConfig,
)
from computronium.execution.task_weights import TASK_GROUPS


@pytest.fixture
def generator(tmp_path: Path) -> CandidateGenerator:
    config = ExecutionStrategyConfig(state=ExperimentState(str(tmp_path / "exp.db")))
    return CandidateGenerator(config)


@pytest.mark.parametrize("task_filter", ["all", "", None])
def test_unfiltered_matches_everything(
    generator: CandidateGenerator, task_filter: str | None
) -> None:
    generator.task_filter = task_filter
    assert generator._matches_filter("mnist")
    assert generator._matches_filter("cartpole")


def test_exact_task_name_matches(generator: CandidateGenerator) -> None:
    generator.task_filter = "mnist"
    assert generator._matches_filter("mnist")
    assert not generator._matches_filter("cartpole")


@pytest.mark.parametrize(
    ("group", "member"),
    sorted(
        (group, member) for group, members in TASK_GROUPS.items() for member in members
    ),
)
def test_group_members_match(
    generator: CandidateGenerator, group: str, member: str
) -> None:
    generator.task_filter = group
    assert generator._matches_filter(member), f"{member!r} should match group {group!r}"


def test_group_excludes_outsiders(generator: CandidateGenerator) -> None:
    generator.task_filter = "vision"
    assert generator._matches_filter("mnist")
    assert not generator._matches_filter("cartpole")


def test_unknown_filter_matches_nothing(generator: CandidateGenerator) -> None:
    generator.task_filter = "not-a-group"
    assert not generator._matches_filter("mnist")
