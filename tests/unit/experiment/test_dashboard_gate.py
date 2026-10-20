"""The dashboard carries the gate's rules (TODO69).

A picture of a run's uncertainty needs the margin the statistical gate
asks for, and the seeds a claim is measured against. Those rules belong
to the gate, and the gate is on the server: the browser must not invent a
margin, and the payload must carry the rules in one place so every view
measures the run the same way.
"""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any

import pytest

from computronium.experiment.execution.dashboard.web import (
    DashboardConfig,
    WebDashboard,
)
from computronium.experiment.execution.statistical_promotion import GateThresholds

if TYPE_CHECKING:
    from pathlib import Path


@pytest.fixture(autouse=True)
def _registries() -> None:
    """The registries the dashboard reads through."""
    from computronium.experiment.schema.seed_registries import seed_all_registries

    seed_all_registries()


def _empty_run(tmp_path: Path) -> tuple[Path, str]:
    """A store holding a run that has measured nothing yet."""
    from computronium.experiment.evidence.store import RecordStore, StoreConfig
    from computronium.experiment.schema.run_spec import RunSpec

    path = tmp_path / "gate.duckdb"
    spec = RunSpec(
        profile="demo",
        task="digits",
        objectives=("validation_accuracy",),
        fidelity="L1",
        n_seeds=2,
        epochs=1,
    )
    with RecordStore(StoreConfig(path=path)) as store:
        return path, store.create_run(spec=spec)


def _metrics(path: Path, run_id: str) -> dict[str, Any]:
    """The metrics the dashboard serves for a run."""
    dashboard = WebDashboard(DashboardConfig(store_path=str(path)))
    return asyncio.run(dashboard._get_campaign_metrics_detailed(run_id))


def test_the_run_carries_the_gate_s_rules(tmp_path: Path) -> None:
    """The thresholds a claim is measured against travel with the run."""
    path, run_id = _empty_run(tmp_path)

    metrics = _metrics(path, run_id)

    gate = metrics["gate"]
    thresholds = GateThresholds()
    assert gate["alpha"] == thresholds.alpha
    assert gate["superiority_margin_sigma"] == thresholds.superiority_margin_sigma
    assert gate["required_seeds_per_group"] == thresholds.required_seeds_per_group
    assert metrics["required_seeds"] == thresholds.required_seeds_per_group


def test_the_rules_are_the_gate_s_own(tmp_path: Path) -> None:
    """The payload does not carry a threshold of its own.

    A view that measured the run against a margin the gate does not use
    would be measuring a different run from the one the report describes.
    """
    path, run_id = _empty_run(tmp_path)

    metrics = _metrics(path, run_id)

    assert metrics["gate"] == GateThresholds().to_dict()
