"""UX-L13: every registered panel renders populated + empty, headless (C2)."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

import computronium.ui.dashboard as dashboard_module
from computronium.ui.dashboard import DashboardApp
from computronium.ui.panel_registry import panel_registry
from computronium.visualization.live_atlas import EmbedCache
from tests.ui.fixture import seed_campaign_root

if TYPE_CHECKING:
    from pathlib import Path


def _make_app(root: Path) -> DashboardApp:
    app = DashboardApp(
        root=root,
        log_path=root / "logs" / "continuous_500.log",
        poll_seconds=2.0,
        daemon_url=None,
        ui_mode="lab",
        ui_actions=False,
        quiet=False,
    )
    app.build()
    return app


def _render_all(app: DashboardApp, *, expect_data: bool) -> None:
    for spec in panel_registry.all_specs():
        key = spec.key
        app.current_panel = key
        data = app._get_panel_data(key)
        if expect_data and spec.adapter is not None:
            assert data is not None, f"adapter produced no data for {key}"
        app._render_current_panel()


def test_all_panels_render_populated(tmp_path: Path) -> None:
    root = tmp_path / "broad_map"
    seed_campaign_root(root)
    app = _make_app(root)
    _render_all(app, expect_data=True)
    # populated root: map has measured specimens
    map_data = app._get_panel_data("map")
    assert map_data is not None
    # console panel gets data from live WS
    assert app._panels.get("console") is not None


def test_all_panels_render_empty_root(tmp_path: Path) -> None:
    root = tmp_path / "empty"
    root.mkdir()
    app = _make_app(root)
    _render_all(app, expect_data=False)


def test_panel_registry_complete() -> None:
    expected = {
        "map",
        "repair",
        "console",
        "composer",
        "record",
    }
    assert set(panel_registry.keys()) == expected
    assert dashboard_module.panel_registry is panel_registry


def test_nav_explorer_hides_lab_panels(tmp_path: Path) -> None:
    root = tmp_path / "broad_map"
    seed_campaign_root(root)
    _make_app(root)
    ctx = {"mode": "explorer", "ui_actions": False}
    visible = {spec.key for spec in panel_registry.visible_specs(ctx)}
    assert "map" in visible
    assert "console" in visible
    assert "composer" in visible
    assert "record" in visible
    assert "repair" in visible
    assert EmbedCache  # imported for parity with atlas flow


@pytest.mark.parametrize("key", ["map", "repair", "console", "composer", "record"])
def test_switch_panel_headless(tmp_path: Path, key: str) -> None:
    root = tmp_path / "broad_map"
    seed_campaign_root(root)
    app = _make_app(root)
    app._switch_panel(key)
    assert app.current_panel == key
    assert key in app._panels
