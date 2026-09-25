"""Scrubber (§4.4) adapter + panel content tests."""

from __future__ import annotations

from typing import TYPE_CHECKING

from computronium.ui.adapters import adapt_scrubber
from computronium.ui.data_adapters import AdapterContext
from computronium.visualization.live_atlas import (
    EmbedCache,
    _objectives_from_heartbeat,
    render_snapshot,
    resolve_log_path,
)
from tests.ui.fixture import seed_campaign_root

if TYPE_CHECKING:
    from pathlib import Path


def _context(root: Path) -> AdapterContext:
    snapshot = render_snapshot(
        root,
        resolve_log_path(root, root / "logs" / "continuous_500.log"),
        EmbedCache(),
        objectives=_objectives_from_heartbeat(root),
        with_atlas=False,
    )
    return AdapterContext(root=root, snapshot=snapshot)


def test_scrubber_parses_fixture_log(tmp_path: Path) -> None:
    root = tmp_path / "broad_map"
    seed_campaign_root(root)
    ctx = _context(root)
    data = adapt_scrubber(ctx.snapshot, root)
    # Fixture log has 40 lines of plain text "line N" — not valid JSON, so 0 events
    assert data.total_lines == 0
    assert data.events == []


def test_scrubber_missing_log(tmp_path: Path) -> None:
    root = tmp_path / "broad_map"
    root.mkdir(parents=True)
    ctx = _context(root)
    data = adapt_scrubber(ctx.snapshot, root)
    assert data.total_lines == 0
    assert data.events == []


def test_scrubber_kind_filtering(tmp_path: Path) -> None:
    root = tmp_path / "broad_map"
    seed_campaign_root(root)
    # Replace fixture log with structured events
    (root / "logs" / "continuous_500.log").write_text(
        "\n".join([
            '{"kind": "state", "state": "training", "timestamp": 1.0}',
            '{"kind": "alert", "alert_kind": "breakthrough", "title": "New high", "body": "acc 0.95", "timestamp": 2.0}',
            '{"kind": "burst_finished", "stop_reason": "target", "timestamp": 3.0}',
        ])
        + "\n",
        encoding="utf-8",
    )
    ctx = _context(root)
    data = adapt_scrubber(ctx.snapshot, root)
    kinds = [e.kind for e in data.events]
    assert kinds == ["state", "alert", "burst_finished"]
    assert data.events[1].is_alert is True
    assert data.events[0].is_alert is False
    assert "TRAINING" in data.events[0].summary
    assert "New high" in data.events[1].summary
    assert "target" in data.events[2].summary


def test_scrubber_panel_renders_headless(tmp_path: Path) -> None:
    from computronium.ui.components.scrubber import ScrubberPanel

    root = tmp_path / "broad_map"
    seed_campaign_root(root)
    ctx = _context(root)
    data = adapt_scrubber(ctx.snapshot, root)

    panel = ScrubberPanel()
    panel.update_data(data)
    element = panel.render()
    assert element is not None
