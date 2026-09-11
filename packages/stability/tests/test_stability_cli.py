"""Smoke test for the ``stability`` CLI."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from stability.cli import main

if TYPE_CHECKING:
    import pytest


def test_statistic_subcommand(capsys: pytest.CaptureFixture[str]) -> None:
    code = main([
        "statistic",
        "--kind",
        "windowed_growth",
        "--gain",
        "1.2",
        "--dim",
        "16",
    ])
    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["kind"] == "windowed_growth"
    assert payload["statistic"] > 1.0
    assert payload["kill"] is True


def test_check_subcommand_stable_map(capsys: pytest.CaptureFixture[str]) -> None:
    code = main(["check", "--gain", "0.1", "--steps", "10", "--dim", "16"])
    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["killed_at"] is None
