"""The run's account of itself: the ledger and the contrast (TODO69).

The stage shows the run as a process and as a judgement. These tests pin the
judgement: every arm the run measured is on the ledger with the gate's
standing on it — including the arms that fell short, which a ledger that
listed only the claims would hide — and the contrast measures the arms
against one another over the cells they share, and says plainly when the
test could not be run.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from fastapi.testclient import TestClient

from computronium.experiment.execution.dashboard.ledger import (
    contrast_payload,
    ledger_payload,
)
from computronium.experiment.execution.dashboard.web import (
    DashboardConfig,
    WebDashboard,
)
from computronium.experiment.execution.events import (
    PipelineEventBus,
    publish_event,
    set_event_bus,
)
from tests.unit.experiment.dashboard_store import demo_record as _record
from tests.unit.experiment.dashboard_store import demo_spec as _spec

if TYPE_CHECKING:
    from pathlib import Path

# The two arms the run measured, and what each of them scored.
ARMS = (("gradient", 0.40), ("pepita", 0.60))


@pytest.fixture(autouse=True)
def _isolated_bus():
    """Every test gets its own bus, so no event leaks between them."""
    set_event_bus(PipelineEventBus())
    yield
    set_event_bus(None)


@pytest.fixture
def store_with_run(tmp_path: Path) -> tuple[Path, str]:
    """A store holding one run: two arms, five measured seeds of each."""
    from computronium.experiment.evidence.store import RecordStore, StoreConfig

    path = tmp_path / "run.duckdb"
    with RecordStore(StoreConfig(path=path)) as store:
        run_id = store.create_run(spec=_spec())
        for credit, score in ARMS:
            for seed in range(5):
                store.append(_record(run_id, score + 0.01 * seed, seed, credit))
    return path, run_id


def _store(path: Path):
    """The store, opened for reading."""
    from computronium.experiment.evidence.store import RecordStore, StoreConfig

    return RecordStore(StoreConfig(path=path, read_only=True))


class TestLedger:
    """Every arm, its evidence, and the gate's standing on it."""

    def test_every_arm_is_on_the_ledger(self, store_with_run) -> None:
        path, run_id = store_with_run
        with _store(path) as store:
            ledger = ledger_payload(store, run_id)

        arms = {arm["value"]: arm for arm in ledger["claims"]}
        assert set(arms) == {"gradient", "pepita"}
        assert arms["pepita"]["mean"] > arms["gradient"]["mean"]
        assert arms["pepita"]["n"] == 5
        assert arms["pepita"]["cells"] == 1

    def test_an_arm_that_fell_short_is_still_on_the_ledger(self, tmp_path) -> None:
        """A ledger that lists only the claims hides the hole they leave."""
        from computronium.experiment.evidence.store import RecordStore, StoreConfig

        path = tmp_path / "short.duckdb"
        with RecordStore(StoreConfig(path=path)) as store:
            run_id = store.create_run(spec=_spec())
            for seed in range(5):
                store.append(_record(run_id, 0.40 + 0.01 * seed, seed, "gradient"))
            # One arm, three seeds: short of the floor, so it backs no claim.
            for seed in range(3):
                store.append(_record(run_id, 0.60, seed, "pepita"))
        with _store(path) as store:
            ledger = ledger_payload(store, run_id)

        arms = {arm["value"]: arm for arm in ledger["claims"]}
        assert arms["pepita"]["verdict"] == "INSUFFICIENT"
        assert arms["gradient"]["verdict"] == "PASSED"

    def test_the_gate_s_own_standing_is_reported(self, store_with_run) -> None:
        path, run_id = store_with_run
        with _store(path) as store:
            ledger = ledger_payload(store, run_id)

        assert ledger["standings"]["PASSED"] == 2

    def test_the_axes_that_did_not_vary_are_named(self, store_with_run) -> None:
        path, run_id = store_with_run
        with _store(path) as store:
            ledger = ledger_payload(store, run_id)

        fixed = {axis["axis"]: axis["value"] for axis in ledger["fixed"]}
        assert fixed["geometry"] == "feedforward"
        assert fixed["dynamics"] == "instantaneous"

    def test_the_report_s_own_limitations_are_quoted(self, store_with_run) -> None:
        """The ledger says why the claims are not more than they are."""
        path, run_id = store_with_run
        with _store(path) as store:
            ledger = ledger_payload(store, run_id)

        assert ledger["limitations"]
        assert all(item["detail"] for item in ledger["limitations"])


class TestContrast:
    """The arms against one another, and the test."""

    def test_the_widest_axis_is_the_one_under_test(self, store_with_run) -> None:
        path, run_id = store_with_run
        with _store(path) as store:
            contrast = contrast_payload(store, run_id)

        assert contrast["axis"] == "credit"
        assert contrast["metric"] == "val_acc"
        assert [arm["value"] for arm in contrast["arms"]] == ["pepita", "gradient"]

    def test_a_pair_is_measured_over_the_cells_it_shares(self, store_with_run) -> None:
        path, run_id = store_with_run
        with _store(path) as store:
            contrast = contrast_payload(store, run_id)

        pair = contrast["pairs"][0]
        assert pair["a"] == "pepita"
        assert pair["b"] == "gradient"
        assert pair["shared_cells"] == 1
        assert pair["difference"] > 0

    def test_a_test_that_cannot_run_says_so(self, store_with_run) -> None:
        """One shared cell is not a test: the verdict must not dress it up."""
        path, run_id = store_with_run
        with _store(path) as store:
            contrast = contrast_payload(store, run_id)

        test = contrast["test"]
        assert test["tested"] is False
        assert test["p_value"] is None
        assert test["shared_cells"] == 1
        assert test["required_cells"] == 2

    def test_no_number_is_a_nan(self, store_with_run) -> None:
        """JSON has no NaN, and the browser cannot read one."""
        import json

        path, run_id = store_with_run
        with _store(path) as store:
            contrast = contrast_payload(store, run_id)

        assert "NaN" not in json.dumps(contrast)


class TestEndpoints:
    """The dashboard serves the account, and the run's stages."""

    def test_the_account_endpoint_carries_the_ledger_and_the_contrast(
        self, store_with_run
    ) -> None:
        path, run_id = store_with_run
        dashboard = WebDashboard(DashboardConfig(store_path=str(path)))
        with TestClient(dashboard.app) as client:
            response = client.get(f"/api/runs/{run_id}/account")

        assert response.status_code == 200
        payload = response.json()
        assert payload["ledger"]["claims"]
        assert payload["contrast"]["arms"]

    @pytest.mark.asyncio
    async def test_the_events_endpoint_carries_the_run_s_stages(self) -> None:
        """The timeline is the run the dashboard watched, stage by stage."""
        dashboard = WebDashboard(DashboardConfig(enable_websockets=False))
        await dashboard.start()
        try:
            publish_event("s6_train", "train cells", run_id="run-1")
            publish_event("s7_measure", "measured a cell", run_id="run-1")
            publish_event("s6_train", "train cells", run_id="other-run")
        finally:
            await dashboard.stop()

        with TestClient(dashboard.app) as client:
            response = client.get("/api/events", params={"run_id": "run-1"})

        payload = response.json()
        assert [event["stage"] for event in payload["events"]] == [
            "s6_train",
            "s7_measure",
        ]
        assert [stage["stage"] for stage in payload["stages"]] == [
            "s6_train",
            "s7_measure",
        ]
        assert payload["stages"][0]["action"] == "train cells"
        assert payload["seconds"] >= 0.0
