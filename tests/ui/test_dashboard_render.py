"""Every registered view renders populated + empty, headless."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from computronium.ui.dashboard import DashboardApp
from computronium.ui.view_registry import registry
from tests.ui.fixture import seed_campaign_root

if TYPE_CHECKING:
    from pathlib import Path


def _make_app(root: Path) -> DashboardApp:
    app = DashboardApp(
        root=root,
        log_path=root / "logs" / "continuous_500.log",
        poll_seconds=2.0,
        daemon_url=None,
    )
    app.build()
    return app


def test_views_are_the_five_navigation_targets() -> None:
    views = registry.get_visible_views()
    view_keys = tuple(v.key for v in views)
    assert view_keys == ("monitor", "atlas", "defects", "evolution", "evidence")


def test_default_view_is_monitor(tmp_path: Path) -> None:
    root = tmp_path / "broad_map"
    seed_campaign_root(root)
    app = _make_app(root)
    assert app.view == "monitor"
    assert "monitor" in app._rendered


def test_all_views_render_populated(tmp_path: Path) -> None:
    root = tmp_path / "broad_map"
    seed_campaign_root(root)
    app = _make_app(root)
    views = registry.get_visible_views()
    for view in views:
        app.switch_view(view.key)
        assert app.view == view.key
        assert view.key in app._rendered

    from computronium.ui.components.monitor import MonitorView

    monitor = app._views["monitor"]
    assert isinstance(monitor, MonitorView)
    assert monitor.data is not None
    assert monitor.data.tiles, "health tiles derived from populated snapshot"


def test_all_views_render_empty_root(tmp_path: Path) -> None:
    root = tmp_path / "empty"
    root.mkdir()
    app = _make_app(root)
    views = registry.get_visible_views()
    for view in views:
        app.switch_view(view.key)
        assert view.key in app._rendered


def test_containers_match_views(tmp_path: Path) -> None:
    root = tmp_path / "broad_map"
    seed_campaign_root(root)
    app = _make_app(root)
    views = registry.get_visible_views()
    view_keys = tuple(v.key for v in views)
    assert set(app._view_containers) == set(view_keys)


@pytest.mark.parametrize("view", registry.get_visible_views())
def test_switch_view_headless(tmp_path: Path, view) -> None:
    root = tmp_path / "broad_map"
    seed_campaign_root(root)
    app = _make_app(root)
    app.switch_view(view.key)
    assert app.view == view.key
    assert view.key in app._views


def test_artifact_change_refreshes_current_view(tmp_path: Path) -> None:
    root = tmp_path / "broad_map"
    seed_campaign_root(root)
    app = _make_app(root)
    (root / "runtime_defects.jsonl").open("a", encoding="utf-8").write(
        '{"defect_id": "new1", "timestamp": 9.0, "task": "t", "cell": "c", '
        '"error_class": "E", "message": "m", "status": "open", "traceback_tail": ""}\n'
    )
    app._poll()
    assert "monitor" in app._rendered
    assert app._snapshot is not None
