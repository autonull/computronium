"""W64: the science CLI dry runs, locked on what they plan.

The analysis and science handlers were 4-6% covered. A dry run is the cheap
contract they all share (TODO46 D22, D6):

* **A dry run prints the command's plan and names itself.**
* **A dry run writes nothing** — no store, no output directory.
* **The stability-plasticity sweep is one declared grid**: the default
  three values on each of five hyperparameters, times one axis per
  structural axis, is 243 cells.
* **The declared hyperparameter names are the harvested names**, so the
  spec validates instead of raising `unknown name(s)` (W69).
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest

from computronium.experiment.surface import cli as surface_cli

if TYPE_CHECKING:
    from pathlib import Path

_ANALYSIS_COMMANDS = (
    ("stability-analysis", ()),
    ("energy-landscape", ()),
    ("nonnormality", ()),
    ("axis-attribution", ()),
    ("counterfactual", ()),
    ("mediation", ()),
    ("pareto-advanced", ()),
    ("seed-variability", ()),
    ("hardware-variance", ("--run-ids", "run-a,run-b")),
    ("repro-advanced", ("--run-id", "run-a")),
)


def _plan(*argv: str, capsys: pytest.CaptureFixture[str]) -> dict:
    assert surface_cli.main([*argv, "--dry-run", "--format", "json"]) == 0
    return json.loads(capsys.readouterr().out)


@pytest.mark.parametrize(("command", "args"), _ANALYSIS_COMMANDS)
def test_an_analysis_dry_run_plans_its_command_and_writes_nothing(
    command: str,
    args: tuple[str, ...],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.chdir(tmp_path)

    plan = _plan(command, *args, capsys=capsys)

    assert plan["command"] == command
    assert not list(tmp_path.glob("*.duckdb"))
    assert not (tmp_path / "benchmark_results").exists()


def test_stability_plasticity_plans_the_declared_sweep(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.chdir(tmp_path)

    plan = _plan("stability-plasticity", capsys=capsys)

    assert plan["command"] == "stability-plasticity"
    assert plan["total_cells"] == 243
    assert plan["axes"] == {
        "substrate": ["digital"],
        "geometry": ["recurrent"],
        "dynamics": ["energy_minimization"],
        "plasticity": ["null"],
        "credit": ["thermodynamic_contrast"],
        "update": ["euclidean"],
    }
    assert not (tmp_path / "sta.duckdb").exists()


def test_frozen_theta_psi_plans_its_coordinate_population(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.chdir(tmp_path)

    plan = _plan("frozen-theta-psi", capsys=capsys)

    assert plan["command"] == "frozen-theta-psi"
    assert plan["total_coordinates"] > 0
    assert plan["substrates"][0] == "digital"
    assert plan["plasticity_types"][0] == "null"
    assert not (tmp_path / "frozen_psi.duckdb").exists()


def test_hypothesis_campaign_plans_the_templates_it_would_read(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.chdir(tmp_path)
    templates = tmp_path / "templates.json"

    plan = _plan("hypothesis-campaign", "--templates", str(templates), capsys=capsys)

    assert plan["command"] == "hypothesis-campaign"
    assert plan["templates"] == str(templates)
    assert plan["bindings"] == []
    assert not templates.exists()
