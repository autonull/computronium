"""The dashboard's run status: measured, not asserted (TODO68).

The mode chip used to be a constant that said EXPLORATORY whatever the run
was. It is now derived from the run's own declaration and the repository's
pre-registered thresholds, so the chip is a reading of the run rather than a
label pasted over it.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import pytest

from computronium.experiment.execution.dashboard.web import run_status
from computronium.experiment.schema.run_spec import RunSpec
from computronium.experiment.schema.seed_registries import seed_all_registries

if TYPE_CHECKING:
    from collections.abc import Coroutine
    from pathlib import Path


@pytest.fixture(autouse=True)
def _registries() -> None:
    """The objective registry the mode is read through."""
    seed_all_registries()


def _spec(*objectives: str) -> RunSpec:
    return RunSpec(
        profile="demo",
        task="digits",
        objectives=objectives,
        fidelity="L1",
        n_seeds=5,
        epochs=1,
    )


def test_an_unregistered_metric_is_exploratory() -> None:
    """The demo's claim metric has no pre-registered threshold."""
    status = run_status(_spec("validation_accuracy"), "run-1", ("val_acc",))

    assert status["mode"] == "EXPLORATORY"
    assert status["profile"] == "demo"
    assert status["tasks"] == ["digits"]
    assert status["fidelity"] == "L1"
    assert status["objectives"] == ["validation_accuracy"]
    assert status["claim_metrics"] == ["val_acc"]


def test_a_preregistered_claim_is_confirmatory(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A metric with a threshold in configs/preregistrations is confirmatory."""
    from computronium.experiment.surface import report

    def _registered(before=None, cells=frozenset()) -> frozenset[str]:
        return frozenset({"val_acc"})

    monkeypatch.setattr(report, "preregistered_metrics", _registered)

    status = run_status(_spec("validation_accuracy"), "run-2", ("val_acc",))

    assert status["mode"] == "PREREGISTERED"


def test_a_run_without_a_spec_is_exploratory() -> None:
    """A run the store cannot describe is not claimed to be confirmatory."""
    status = run_status(None, "run-3")

    assert status["mode"] == "EXPLORATORY"
    assert status["profile"] is None
    assert status["tasks"] == []


def test_the_metrics_carry_the_run(tmp_path: Path) -> None:
    """The payload the clients read says which run it is about."""
    from computronium.experiment.evidence.store import RecordStore, StoreConfig
    from computronium.experiment.execution.dashboard.web import (
        DashboardConfig,
        WebDashboard,
    )
    from computronium.experiment.schema.coordinate import (
        Coordinate,
        Provenance,
        Schedule,
    )
    from computronium.experiment.schema.record import (
        FailureCause,
        GateVerdict,
        Maturity,
        Record,
        ReproducibilityClass,
        Severity,
        Status,
    )

    path = tmp_path / "run.duckdb"
    spec = _spec("validation_accuracy")

    with RecordStore(StoreConfig(path=path)) as store:
        run_id = store.create_run(spec=spec)
        store.append(
            Record.create(
                run_id=run_id,
                coordinate=Coordinate(
                    substrate="digital",
                    geometry="feedforward",
                    dynamics="instantaneous",
                    plasticity="null",
                    credit="gradient",
                    update="euclidean",
                    params={},
                ),
                schedule=Schedule(
                    fidelity="L1",
                    seed=0,
                    n_seeds=5,
                    epochs=1,
                    batch_limit=0,
                    budget_id="dashboard-test",
                    task_id="digits",
                    param_budget=0,
                ),
                provenance=Provenance(
                    env={"python": "3.14", "platform": "linux"},
                    dataset="digits",
                    dataset_version="1.0",
                    code_sha="dashboard-test",
                    policy="dashboard-test",
                    links={"run_id": run_id},
                ),
                status=Status(
                    gate_verdict=GateVerdict.PASS_,
                    defect="",
                    cause=FailureCause.UNKNOWN,
                    severity=Severity.LOW,
                    quarantine=False,
                    maturity=Maturity.L1,
                    uncertainty={},
                    reproducibility=ReproducibilityClass.REPLAYABLE,
                    assessment_procedure_version="1.0",
                    ceec_link=None,
                ),
                payload={
                    "val_acc": 0.42,
                    "walltime_s": 1.5,
                    "param_count": 1024,
                },
            )
        )

    dashboard = WebDashboard(DashboardConfig(store_path=str(path)))
    payload = asyncio_run(dashboard._get_campaign_metrics_detailed(run_id))

    assert payload["run"]["mode"] == "EXPLORATORY"
    assert payload["run"]["profile"] == "demo"
    assert payload["run"]["run_id"] == run_id


def asyncio_run[T](coro: Coroutine[Any, Any, T]) -> T:
    """Run one coroutine to completion."""
    import asyncio

    return asyncio.run(coro)
