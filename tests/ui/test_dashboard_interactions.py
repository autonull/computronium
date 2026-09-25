"""WS fan-out — app-level streams."""

from __future__ import annotations

from typing import TYPE_CHECKING

from computronium.ui.dashboard import DashboardApp
from computronium.ui.event_bus import WebSocketEvent, event_bus
from tests.ui.fixture import seed_campaign_root

if TYPE_CHECKING:
    from pathlib import Path


def _make_app(root: Path) -> DashboardApp:
    app = DashboardApp(
        root=root,
        log_path=None,
        poll_seconds=2.0,
        daemon_url=None,
    )
    app.build()
    return app


def test_ws_events_route_to_feed_and_reports(tmp_path: Path) -> None:
    root = tmp_path / "broad_map"
    seed_campaign_root(root)
    app = _make_app(root)

    raw = {
        "kind": "alert",
        "alert_kind": "breakthrough",
        "title": "Test",
        "body": "Test alert",
    }
    app._route_ws_events(raw, now=1234.0)
    assert len(app.event_history) == 1
    assert app.event_history[0].summary
    assert len(app.reports) == 1
    assert app.reports[0].sentence == app.event_history[0].summary


def test_ws_proposal_batch_sets_driver_intent(tmp_path: Path) -> None:
    root = tmp_path / "broad_map"
    seed_campaign_root(root)
    app = _make_app(root)

    app._route_ws_events(
        {"kind": "proposal_batch", "n_proposals": 3, "dynamics": "spiking"},
        now=1234.0,
    )
    assert app.intent is not None
    assert app.intent.proposing == 3
    assert app.intent.strategy_hint == "spiking"


def test_ws_defect_quarantined_increments_session_delta(tmp_path: Path) -> None:
    root = tmp_path / "broad_map"
    seed_campaign_root(root)
    app = _make_app(root)

    app._route_ws_events({"kind": "defect_quarantined"}, now=1234.0)
    assert app.session_delta.crashes == 1


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


def test_ws_telemetry_appends_loss(tmp_path: Path) -> None:
    root = tmp_path / "broad_map"
    seed_campaign_root(root)
    app = _make_app(root)

    app._route_ws_telemetry({"train_loss": 0.42})
    assert app.loss_history[-1] == 0.42


def test_bus_publish_reaches_dashboard_handler(tmp_path: Path) -> None:
    root = tmp_path / "broad_map"
    seed_campaign_root(root)
    app = _make_app(root)

    event_bus.publish(
        WebSocketEvent(topic="events", payload={"kind": "cell_done", "cell": "x"})
    )
    assert len(app.event_history) == 1
