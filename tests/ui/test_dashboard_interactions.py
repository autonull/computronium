"""UX-L14 + live-stream routing: mode toggle re-render, WS fan-out, glossary (C3)."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

from computronium.ui.dashboard import DashboardApp
from computronium.ui.event_bus import ModeChanged, WebSocketEvent, event_bus
from computronium.ui.glossary_service import get_glossary_service
from computronium.ui.mode_toggle import get_mode, set_mode
from tests.ui.fixture import seed_campaign_root

if TYPE_CHECKING:
    from pathlib import Path

    from computronium.ui.components.activity_feed import ActivityFeed
    from computronium.ui.components.field_reports import FieldReports


def _make_app(root: Path) -> DashboardApp:
    app = DashboardApp(
        root=root,
        log_path=None,
        poll_seconds=2.0,
        daemon_url=None,
        ui_mode="auto",
        gamify=True,
        ui_actions=False,
        rebuild_state=False,
    )
    app.build()
    return app


def test_mode_toggle_publishes_and_rerenders(tmp_path: Path) -> None:
    root = tmp_path / "broad_map"
    seed_campaign_root(root)
    _make_app(root)
    events: list[ModeChanged] = []
    unsub = event_bus.subscribe(ModeChanged, events.append)

    try:
        set_mode("lab")
        assert get_mode() == "lab"
        assert [e.mode for e in events] == ["lab"]
        set_mode("lab")  # no-op: same register
        assert len(events) == 1
        set_mode("explorer")
        assert [e.mode for e in events] == ["lab", "explorer"]
    finally:
        unsub()
        set_mode("explorer", persist=False) if get_mode() != "explorer" else None


def test_ws_events_route_to_feed_and_reports(tmp_path: Path) -> None:
    root = tmp_path / "broad_map"
    seed_campaign_root(root)
    app = _make_app(root)
    # instantiate the consumer panels
    app._get_panel("activity_feed")
    app._get_panel("field_reports")

    raw = {"kind": "burst_complete", "cell": "a|b|c|d"}
    app._route_ws_events(raw, now=1234.0)
    assert len(app.event_history) == 1

    feed = cast("ActivityFeed", app._panels["activity_feed"])
    reports = cast("FieldReports", app._panels["field_reports"])
    assert len(feed.events) == 1
    assert feed.events[0].summary
    assert len(reports.reports) == 1
    assert reports.reports[0].sentence == feed.events[0].summary


def test_ws_telemetry_throttled_paint(tmp_path: Path) -> None:
    root = tmp_path / "broad_map"
    seed_campaign_root(root)
    app = _make_app(root)
    app.loss_history = [1.0, 0.9]

    app._route_ws_telemetry({})
    first_paint = app._last_ws_paint
    app._route_ws_telemetry({})  # within 2s window: throttled
    assert app._last_ws_paint == first_paint

    app._last_ws_paint -= DashboardApp._WS_PAINT_INTERVAL_S + 0.1
    app._route_ws_telemetry({})
    assert app._last_ws_paint > first_paint


def test_bus_publish_reaches_dashboard_handler(tmp_path: Path) -> None:
    root = tmp_path / "broad_map"
    seed_campaign_root(root)
    app = _make_app(root)
    app._get_panel("activity_feed")

    event_bus.publish(
        WebSocketEvent(topic="events", payload={"kind": "cell_done", "cell": "x"})
    )
    assert len(app.event_history) == 1
    assert len(cast("ActivityFeed", app._panels["activity_feed"]).events) == 1


def test_glossary_covers_dashboard_keys() -> None:
    service = get_glossary_service()
    assert service.has("loss_curve")
    entries = service.all_entries()
    assert entries, "glossary loaded"
    for entry in entries.values():
        assert entry.explorer and entry.lab
