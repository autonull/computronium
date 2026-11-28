"""W64: the campaign CLI's inventory and refusals, locked on their contracts.

The campaign handlers were 6% covered. The coverage inventory commands are
read-only and decide what the registry holds (D6):

* **`coverage tasks` is the registry's own table**: every row names its
  task, domain and the objectives it emits and does not.
* **An unknown domain is refused by name**, and the refusal lists the valid
  domains.
* **`coverage unmeasured` is a mapping from task to the objectives it
  cannot emit.**
* **A campaign file that does not exist is refused by name**, not loaded.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from computronium.experiment.surface import cli as surface_cli

if TYPE_CHECKING:
    from pathlib import Path

    import pytest


def _main(*argv: str) -> int:
    return surface_cli.main(list(argv))


def test_coverage_tasks_lists_the_registrys_objectives(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert _main("coverage", "tasks", "--format", "json") == 0
    tasks = json.loads(capsys.readouterr().out)

    assert tasks
    for task in tasks:
        assert {"name", "domain", "cost_class"} <= task.keys()
        assert isinstance(task["measured_objectives"], list)
        assert isinstance(task["unmeasured_objectives"], list)
        assert not set(task["measured_objectives"]) & set(task["unmeasured_objectives"])


def test_coverage_tasks_filters_a_domain(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert _main("coverage", "tasks", "--domain", "vision", "--format", "json") == 0
    tasks = json.loads(capsys.readouterr().out)

    assert tasks
    assert {task["domain"] for task in tasks} == {"vision"}


def test_coverage_tasks_refuses_an_unknown_domain_by_name(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert _main("coverage", "tasks", "--domain", "nope") == 1
    text = capsys.readouterr().out

    assert "nope" in text
    assert "vision" in text


def test_coverage_unmeasured_is_a_task_to_objective_mapping(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert _main("coverage", "unmeasured", "--format", "json") == 0
    report = json.loads(capsys.readouterr().out)

    assert isinstance(report, dict)
    for task_name, objectives in report.items():
        assert isinstance(task_name, str)
        assert isinstance(objectives, list)


def test_a_campaign_file_that_does_not_exist_is_refused_by_name(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    campaign = tmp_path / "absent.yaml"

    assert _main("campaign", str(campaign)) == 1
    assert "absent.yaml" in capsys.readouterr().err
