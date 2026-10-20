"""The run's flow, and what it can attribute (TODO69).

The stage shows the run as a process and as a judgement. These tests pin
both: the flow reads the run's own events — the stages it reached, the
counts each one reported, what the gate refused — and the attribution says
which axes moved the objective, and says plainly when the run's design is
too small to say.

The rules come from the server: the counts are the events' own, the arms are
the records' own, and the browser draws what it is given.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import pytest
from fastapi.testclient import TestClient

from computronium.experiment.execution.dashboard.attribution import (
    attribution_payload,
)
from computronium.experiment.execution.dashboard.flow import flow_payload
from computronium.experiment.execution.dashboard.web import (
    DashboardConfig,
    WebDashboard,
)
from tests.unit.experiment.dashboard_store import demo_record as _record
from tests.unit.experiment.dashboard_store import demo_spec as _spec

if TYPE_CHECKING:
    from pathlib import Path


def _event(stage: str, detail: dict[str, Any] | None = None) -> dict[str, Any]:
    """One event frame, as the dashboard keeps it."""
    return {
        "stage": stage,
        "message": stage,
        "level": "ok",
        "run_id": "run-1",
        "detail": detail or {},
        "at": 0.0,
    }


def _announcement(stage: str, proposals: int = 0, records: int = 0) -> dict[str, Any]:
    """A stage saying what it produced."""
    return _event(stage, {"proposals": proposals, "records": records})


def _store(path: Path):
    """The store, opened for reading."""
    from computronium.experiment.evidence.store import RecordStore, StoreConfig

    return RecordStore(StoreConfig(path=path, read_only=True))


@pytest.fixture
def store_with_run(tmp_path: Path) -> tuple[Path, str]:
    """A store holding one run: two credit arms, five measured seeds of each."""
    from computronium.experiment.evidence.store import RecordStore, StoreConfig

    path = tmp_path / "run.duckdb"
    with RecordStore(StoreConfig(path=path)) as store:
        run_id = store.create_run(spec=_spec())
        for credit, score in (("gradient", 0.40), ("pepita", 0.60)):
            for seed in range(5):
                store.append(_record(run_id, score + 0.01 * seed, seed, credit))
    return path, run_id


class TestFlow:
    """The run's cells, from the space to the evidence."""

    def test_the_stages_are_the_run_s_own(self) -> None:
        events = [
            _announcement("s3_schedule", proposals=4),
            _announcement("s4_gate", proposals=4),
            _announcement("s6_train", proposals=4),
        ]
        flow = flow_payload(events, "run-1")

        assert [stage["stage"] for stage in flow["stages"]] == [
            "s3_schedule",
            "s4_gate",
            "s6_train",
        ]
        assert flow["stages"][0]["action"] == "schedule cells"

    def test_the_counts_are_the_events_own(self) -> None:
        flow = flow_payload([_announcement("s3_schedule", proposals=4)], "run-1")

        stage = flow["stages"][0]
        assert stage["count"] == 4
        assert stage["kind"] == "cells"

    def test_a_stage_that_ran_twice_held_the_same_cells(self) -> None:
        """The cells are the peak, not the sum: a second round is the same cells."""
        events = [
            _announcement("s3_schedule", proposals=4),
            _announcement("s3_schedule", proposals=4),
        ]
        flow = flow_payload(events, "run-1")

        assert flow["stages"][0]["count"] == 4
        assert flow["cells"] == 4

    def test_the_measurements_are_counted_as_records(self) -> None:
        """A measurement says which cell it measured; twenty of them are evidence."""
        events = [
            _event("s7_measure", {"cell": "gradient/feedforward/instantaneous"}),
            _event("s7_measure", {"cell": "gradient/feedforward/instantaneous"}),
            _event("s7_measure", {"cell": "pepita/feedforward/instantaneous"}),
        ]
        flow = flow_payload(events, "run-1")

        stage = flow["stages"][0]
        assert stage["count"] == 3
        assert stage["kind"] == "records"
        assert flow["measured"] == 2

    def test_the_gate_s_refusals_are_reported(self) -> None:
        """What the gate threw away is part of the run's shape."""
        events = [_announcement("s4_gate", proposals=3)]
        events[0]["detail"]["refused"] = 1
        flow = flow_payload(events, "run-1")

        assert flow["stages"][0]["refused"] == 1
        assert flow["refused"] == 1
        assert "the gate refused one" in flow["summary"]

    def test_the_summary_says_what_the_run_did(self) -> None:
        events = [
            _announcement("s3_schedule", proposals=4),
            _announcement("s4_gate", proposals=4),
            _event("s8_record", {"records": 20}),
        ]
        flow = flow_payload(events, "run-1")

        assert flow["cells"] == 4
        assert flow["records"] == 20
        assert "four cells" in flow["summary"]
        assert "twenty records" in flow["summary"]

    def test_a_run_this_dashboard_did_not_watch_has_no_flow(self) -> None:
        """The events are process-local: a run from elsewhere has no stages here."""
        flow = flow_payload([], "run-1")

        assert flow["stages"] == []
        assert "did not watch" in flow["summary"]


class TestAttribution:
    """What the run can attribute, and what its design cannot say."""

    def test_the_axis_that_varied_is_named(self, store_with_run) -> None:
        path, run_id = store_with_run
        with _store(path) as store:
            attribution = attribution_payload(store, run_id)

        assert attribution["varied_axes"] == ["credit"]
        assert attribution["held_axes"]
        assert attribution["metric"] == "val_acc"

    def test_the_spread_is_the_arms_own(self, store_with_run) -> None:
        path, run_id = store_with_run
        with _store(path) as store:
            attribution = attribution_payload(store, run_id)

        credit = next(axis for axis in attribution["axes"] if axis["axis"] == "credit")
        assert credit["varied"] is True
        assert credit["spread"] > 0
        assert {arm["value"] for arm in credit["values"]} == {"gradient", "pepita"}

    def test_a_run_that_varied_one_axis_cannot_attribute(self, store_with_run) -> None:
        """One varied axis cannot say which of two things mattered: there was one."""
        path, run_id = store_with_run
        with _store(path) as store:
            attribution = attribution_payload(store, run_id)

        assert attribution["attributable"] is False
        assert "can speak about credit alone" in attribution["reason"]

    def test_a_run_that_varied_two_axes_can(self, tmp_path) -> None:
        """Two varied axes: the run can say which of them moved the objective."""
        from computronium.experiment.evidence.store import RecordStore, StoreConfig

        path = tmp_path / "two.duckdb"
        with RecordStore(StoreConfig(path=path)) as store:
            run_id = store.create_run(spec=_spec())
            for credit, score in (("gradient", 0.40), ("pepita", 0.60)):
                for geometry, offset in (("feedforward", 0.0), ("recurrent", 0.05)):
                    for seed in range(5):
                        store.append(
                            _record(
                                run_id,
                                score + offset + 0.01 * seed,
                                seed,
                                credit,
                                geometry,
                            )
                        )
        with _store(path) as store:
            attribution = attribution_payload(store, run_id)

        assert sorted(attribution["varied_axes"]) == ["credit", "geometry"]
        assert attribution["attributable"] is True

    def test_an_axis_that_was_held_fixed_carries_its_one_value(
        self, store_with_run
    ) -> None:
        path, run_id = store_with_run
        with _store(path) as store:
            attribution = attribution_payload(store, run_id)

        geometry = next(
            axis for axis in attribution["axes"] if axis["axis"] == "geometry"
        )
        assert geometry["varied"] is False
        assert geometry["spread"] == 0
        assert [arm["value"] for arm in geometry["values"]] == ["feedforward"]


class TestEndpoints:
    """The dashboard serves the flow and the attribution."""

    @pytest.mark.asyncio
    async def test_the_flow_endpoint_carries_the_run_s_stages(self) -> None:
        from computronium.experiment.execution.events import (
            PipelineEventBus,
            publish_event,
            set_event_bus,
        )

        set_event_bus(PipelineEventBus())
        try:
            dashboard = WebDashboard(DashboardConfig(enable_websockets=False))
            await dashboard.start()
            try:
                publish_event(
                    "s4_gate",
                    "gate proposals: 4 proposals",
                    run_id="run-1",
                    detail={"proposals": 4, "records": 0, "refused": 1},
                )
            finally:
                await dashboard.stop()
        finally:
            set_event_bus(None)

        with TestClient(dashboard.app) as client:
            response = client.get("/api/runs/run-1/flow")

        payload = response.json()
        assert payload["stages"][0]["stage"] == "s4_gate"
        assert payload["refused"] == 1

    def test_the_attribution_endpoint_carries_the_arms(self, store_with_run) -> None:
        path, run_id = store_with_run
        dashboard = WebDashboard(DashboardConfig(store_path=str(path)))
        with TestClient(dashboard.app) as client:
            response = client.get(f"/api/runs/{run_id}/attribution")

        assert response.status_code == 200
        payload = response.json()
        assert payload["varied_axes"] == ["credit"]
        assert payload["attributable"] is False
