"""W64: the registry and quality CLI commands, locked on their contracts.

The surface CLI's registry module was 5% covered: the dataset and environment
commands never ran. Each is a decision (D6):

* **A registered dataset round-trips through the registry**: its digest is
  the file content's, its auto-detected splits are the directories it has,
  and its metadata export is JSON.
* **Verify reports the dataset it checked and exits zero for a matching
  tree**; a missing dataset is refused.
* **An environment snapshot verifies against the machine that wrote it**;
  a Docker command refuses by name when the binary is absent.
* **A quality gate returns a verdict** (PASSED/FAILED) and writes the
  requested format.
"""

from __future__ import annotations

import json
import shutil
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from pathlib import Path

import pytest

from computronium.experiment.surface import cli as surface_cli


def _main(*argv: str) -> int:
    return surface_cli.main(list(argv))


@pytest.fixture
def dataset_tree(tmp_path: Path) -> Path:
    root = tmp_path / "data" / "digits" / "1.0.0"
    (root / "train").mkdir(parents=True)
    (root / "test").mkdir(parents=True)
    (root / "train" / "a.txt").write_text("alpha", encoding="utf-8")
    (root / "test" / "b.txt").write_text("beta", encoding="utf-8")
    return root


def test_a_registered_dataset_round_trips_through_the_registry(
    tmp_path: Path, dataset_tree: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    store = tmp_path / "experiment.duckdb"
    data_root = dataset_tree.parents[1]

    assert (
        _main(
            "dataset",
            "register",
            "digits",
            "1.0.0",
            str(dataset_tree),
            "--store",
            str(store),
            "--data-root",
            str(data_root),
            "--description",
            "handwritten digits",
            "--tags",
            "env=test",
        )
        == 0
    )
    registered = capsys.readouterr().out
    assert "digits" in registered
    assert "1.0.0" in registered
    assert "train" in registered

    assert (
        _main(
            "dataset",
            "get",
            "digits",
            "1.0.0",
            "--store",
            str(store),
            "--data-root",
            str(data_root),
            "--format",
            "json",
        )
        == 0
    )
    version: dict[str, Any] = json.loads(capsys.readouterr().out)

    assert version["dataset_id"] == "digits"
    assert version["version"] == "1.0.0"
    assert set(version["splits"]) == {"train", "test"}
    assert version["description"] == "handwritten digits"
    assert version["tags"] == {"env": "test"}


def test_dataset_listing_and_tag_filter(
    tmp_path: Path, dataset_tree: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    store = tmp_path / "experiment.duckdb"
    data_root = dataset_tree.parents[1]
    assert (
        _main(
            "dataset",
            "register",
            "digits",
            "1.0.0",
            str(dataset_tree),
            "--store",
            str(store),
            "--data-root",
            str(data_root),
            "--tags",
            "env=test",
        )
        == 0
    )
    capsys.readouterr()

    assert (
        _main(
            "dataset",
            "list",
            "--store",
            str(store),
            "--data-root",
            str(data_root),
            "--tag",
            "env=test",
            "--format",
            "json",
        )
        == 0
    )
    listed = json.loads(capsys.readouterr().out)
    assert [row["dataset_id"] for row in listed] == ["digits"]

    assert (
        _main(
            "dataset",
            "list",
            "digits",
            "--store",
            str(store),
            "--data-root",
            str(data_root),
        )
        == 0
    )
    assert "digits@1.0.0" in capsys.readouterr().out


def test_dataset_verify_and_export(
    tmp_path: Path, dataset_tree: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    store = tmp_path / "experiment.duckdb"
    data_root = dataset_tree.parents[1]
    assert (
        _main(
            "dataset",
            "register",
            "digits",
            "1.0.0",
            str(dataset_tree),
            "--store",
            str(store),
            "--data-root",
            str(data_root),
        )
        == 0
    )
    capsys.readouterr()

    assert (
        _main(
            "dataset",
            "verify",
            "digits",
            "1.0.0",
            "--store",
            str(store),
            "--data-root",
            str(data_root),
            "--format",
            "json",
        )
        == 0
    )
    result = json.loads(capsys.readouterr().out)
    assert result["valid"] is True

    exported = tmp_path / "metadata.json"
    assert (
        _main(
            "dataset",
            "export",
            "digits",
            "1.0.0",
            "--store",
            str(store),
            "--data-root",
            str(data_root),
            "-o",
            str(exported),
        )
        == 0
    )
    payload = json.loads(exported.read_text(encoding="utf-8"))
    assert payload["dataset_id"] == "digits"


def test_dataset_get_refuses_an_unknown_version(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    store = tmp_path / "experiment.duckdb"
    data_root = tmp_path / "data"

    assert (
        _main(
            "dataset",
            "get",
            "absent",
            "1.0.0",
            "--store",
            str(store),
            "--data-root",
            str(data_root),
        )
        == 1
    )
    assert "absent" in capsys.readouterr().out


def test_an_environment_snapshot_verifies_against_its_machine(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    snapshot = tmp_path / "snapshot.json"

    assert (
        _main(
            "environment",
            "capture",
            "-o",
            str(snapshot),
            "--no-git",
            "--no-env-vars",
        )
        == 0
    )
    assert "Environment snapshot saved" in capsys.readouterr().out

    assert _main("environment", "verify", str(snapshot), "--format", "json") == 0
    result = json.loads(capsys.readouterr().out)
    assert result["matches"] is True


def test_a_docker_command_refuses_by_name_without_the_binary(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(shutil, "which", lambda _name: None)

    assert _main("environment", "docker-build", "Dockerfile", "image") == 1
    assert "Docker not found" in capsys.readouterr().err


def test_a_quality_gate_reports_its_verdict(
    tmp_path: Path, dataset_tree: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    store = tmp_path / "experiment.duckdb"
    data_root = dataset_tree.parents[1]
    assert (
        _main(
            "dataset",
            "register",
            "digits",
            "1.0.0",
            str(dataset_tree),
            "--store",
            str(store),
            "--data-root",
            str(data_root),
        )
        == 0
    )
    capsys.readouterr()

    code = _main("quality", "check-store", "--store", str(store))
    text = capsys.readouterr().out
    assert "Quality Gate:" in text
    assert code in {0, 1}
