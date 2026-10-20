"""Live pipeline events and the dashboard's forwarding of them (TODO68).

The live rail used to render a hardcoded line every two seconds. These tests
pin the replacement: real producers, real forwarding, and no double reporting.
"""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, cast

import pytest

from computronium.experiment.execution.dashboard.web import (
    DashboardConfig,
    WebDashboard,
)
from computronium.experiment.execution.events import (
    STAGE_ACTIONS,
    PipelineEvent,
    PipelineEventBus,
    get_event_bus,
    publish_event,
    set_event_bus,
)
from computronium.experiment.execution.stage import StageId

if TYPE_CHECKING:
    from fastapi import WebSocket


class _FakeSocket:
    """A WebSocket stand-in that records what the dashboard sends."""

    def __init__(self) -> None:
        self.messages: list[dict] = []

    async def send_json(self, message: dict) -> None:
        self.messages.append(message)


@pytest.fixture(autouse=True)
def _isolated_bus():
    """Every test gets its own bus, so no event leaks between them."""
    set_event_bus(PipelineEventBus())
    yield
    set_event_bus(None)


class TestEventBus:
    """The bus is the one place events are published and observed."""

    def test_subscribers_receive_events(self) -> None:
        received: list[PipelineEvent] = []
        bus = get_event_bus()
        bus.subscribe(received.append)

        publish_event("s7_measure", "pepita seed 0: val_acc 0.456")

        assert len(received) == 1
        assert received[0].stage == "s7_measure"
        assert received[0].message == "pepita seed 0: val_acc 0.456"
        assert received[0].level == "ok"

    def test_unsubscribe_stops_delivery(self) -> None:
        received: list[PipelineEvent] = []
        unsubscribe = get_event_bus().subscribe(received.append)

        publish_event("s6_train", "train cells")
        unsubscribe()
        publish_event("s6_train", "train cells")

        assert len(received) == 1

    def test_a_broken_subscriber_cannot_break_the_run(self) -> None:
        received: list[PipelineEvent] = []
        bus = get_event_bus()

        def explode(_event: PipelineEvent) -> None:
            raise RuntimeError("subscriber is broken")

        bus.subscribe(explode)
        bus.subscribe(received.append)

        publish_event("s8_record", "recorded 4 cells")

        assert len(received) == 1

    def test_every_stage_has_an_action(self) -> None:
        """The rail's vocabulary must cover every stage the pipeline can run."""
        for stage in StageId:
            assert stage.value in STAGE_ACTIONS, f"{stage.value} has no action"

    def test_event_payload_carries_the_wire_shape(self) -> None:
        message = PipelineEvent(
            stage="s8_record",
            message="recorded 4 cells",
            level="warn",
            run_id="abc123",
        ).to_message()

        assert message["type"] == "pipeline_event"
        assert message["stage"] == "s8_record"
        assert message["level"] == "warn"
        assert message["run_id"] == "abc123"
        assert message["timestamp"]


class TestDashboardForwarding:
    """The dashboard is the only thing that turns events into WebSocket frames."""

    @pytest.mark.asyncio
    async def test_events_reach_connected_clients(self) -> None:
        dashboard = WebDashboard(DashboardConfig(enable_websockets=False))
        socket = _FakeSocket()
        dashboard._connected_websockets.add(cast("WebSocket", socket))

        await dashboard.start()
        try:
            publish_event("s7_measure", "pepita seed 0: val_acc 0.456")
            await asyncio.sleep(0.05)
        finally:
            await dashboard.stop()

        frames = [m for m in socket.messages if m.get("type") == "pipeline_event"]
        assert len(frames) == 1
        assert frames[0]["message"] == "pepita seed 0: val_acc 0.456"
        assert frames[0]["stage"] == "s7_measure"

    @pytest.mark.asyncio
    async def test_a_late_client_sees_what_happened(self) -> None:
        """The rail shows the run's story even if the page opened late."""
        dashboard = WebDashboard(DashboardConfig(enable_websockets=False))

        await dashboard.start()
        try:
            publish_event("s8_record", "recorded 4 cells")
            await asyncio.sleep(0.05)
        finally:
            await dashboard.stop()

        socket = _FakeSocket()
        await dashboard._replay_events(cast("WebSocket", socket))

        assert [m["message"] for m in socket.messages] == ["recorded 4 cells"]

    @pytest.mark.asyncio
    async def test_every_event_frame_carries_its_sentence(self) -> None:
        """The browser never writes a sentence: the frame carries it (TODO69).

        The caption renders what the server said, so the words on the screen,
        in the rail and in the account an agent reads are the same words.
        """
        dashboard = WebDashboard(DashboardConfig(enable_websockets=False))
        socket = _FakeSocket()
        dashboard._connected_websockets.add(cast("WebSocket", socket))

        await dashboard.start()
        try:
            publish_event("s7_measure", "pepita seed 0: val_acc 0.456")
            await asyncio.sleep(0.05)
        finally:
            await dashboard.stop()

        frames = [m for m in socket.messages if m.get("type") == "pipeline_event"]
        assert len(frames) == 1
        assert frames[0]["sentence"]
        assert frames[0]["sentence"].endswith(".")

    @pytest.mark.asyncio
    async def test_the_frame_and_the_account_say_the_same_thing(self) -> None:
        """One account: the caption, the rail and the reader agree."""
        dashboard = WebDashboard(DashboardConfig(enable_websockets=False))
        socket = _FakeSocket()
        dashboard._connected_websockets.add(cast("WebSocket", socket))

        await dashboard.start()
        try:
            publish_event("s7_measure", "pepita seed 0: val_acc 0.456")
            await asyncio.sleep(0.05)
        finally:
            await dashboard.stop()

        frame = next(m for m in socket.messages if m.get("type") == "pipeline_event")
        account = await dashboard._narration_payload()

        assert account["lines"][-1]["text"] == frame["sentence"]
        assert frame["sentence"] in account["script"]

    @pytest.mark.asyncio
    async def test_a_run_is_not_reported_twice(self) -> None:
        """A run that speaks for itself is not also counted by the store."""
        dashboard = WebDashboard(DashboardConfig(enable_websockets=False))
        received: list[PipelineEvent] = []
        get_event_bus().subscribe(received.append)

        await dashboard.start()
        try:
            publish_event("s7_measure", "pepita seed 0: val_acc 0.456", run_id="run-1")
            await asyncio.sleep(0.05)

            # Baseline: what the store held when the dashboard first looked.
            dashboard._announce_store_progress({"run-1": 4, "run-2": 0})
            received.clear()

            dashboard._announce_store_progress({"run-1": 8, "run-2": 4})
        finally:
            await dashboard.stop()

        reported = [event.run_id for event in received]
        assert "run-1" not in reported
        assert "run-2" in reported

    @pytest.mark.asyncio
    async def test_store_progress_counts_only_new_records(self) -> None:
        dashboard = WebDashboard(DashboardConfig(enable_websockets=False))
        received: list[PipelineEvent] = []
        get_event_bus().subscribe(received.append)

        await dashboard.start()
        try:
            dashboard._announce_store_progress({"run-3": 4})
            received.clear()
            dashboard._announce_store_progress({"run-3": 4})
            assert received == []
            dashboard._announce_store_progress({"run-3": 7})
        finally:
            await dashboard.stop()
        assert len(received) == 1
        assert "3 new cells" in received[0].message
