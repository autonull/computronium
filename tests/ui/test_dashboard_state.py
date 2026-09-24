"""X4 multi-root + X5 config hot-reload (behavioral, headless)."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from computronium.ui.dashboard import DashboardApp
from computronium.ui.event_bus import ConfigChanged, event_bus
from tests.ui.fixture import seed_campaign_root

if TYPE_CHECKING:
    from pathlib import Path


def _make_app(root: Path, **kwargs: object) -> DashboardApp:
    params: dict[str, object] = {
        "root": root,
        "log_path": None,
        "poll_seconds": 2.0,
        "daemon_url": None,
        "ui_mode": "auto",
        "ui_actions": False,
        "quiet": False,
    }
    params.update(kwargs)
    app = DashboardApp(**params)  # type: ignore[arg-type]
    app.build()
    return app


def test_multi_root_switch_resets_state(tmp_path: Path) -> None:
    """X4: switch_root swaps caches/panels/signature per root."""
    from computronium.visualization.live_atlas import watch_signature

    root_a = tmp_path / "root_a"
    root_b = tmp_path / "root_b"
    seed_campaign_root(root_a)
    seed_campaign_root(root_b)

    app = _make_app(root_a, roots=(root_a, root_b))
    app._switch_panel("map")
    assert "map" in app._panels
    old_map = app._panels["map"]

    app.switch_root(root_b)
    assert app.root == root_b
    # Per-root reset: old instances discarded; the re-render lazily builds a
    # fresh panel bound to root_b.
    assert app._panels.get("map") is not old_map, "panel instances are per-root"
    assert app.current_panel == "map"
    assert app.last_signature == watch_signature(root_b)
    assert app.log_path is not None and root_b in app.log_path.parents

    app.switch_root(root_a)
    assert app.root == root_a


def test_parse_roots_comma_list() -> None:
    from pathlib import Path

    from computronium.cli.dashboard import parse_roots

    assert parse_roots("artifacts/one, artifacts/two") == (
        Path("artifacts/one"),
        Path("artifacts/two"),
    )
    assert parse_roots("  ") == (Path("artifacts/broad_map"),)


def test_config_hot_reload_publishes_new_objectives(tmp_path: Path) -> None:
    """X5: heartbeat.json change re-parses objectives and pushes ConfigChanged."""
    from computronium.autoscientist.objectives import objective_names

    root = tmp_path / "hot_root"
    seed_campaign_root(root)
    app = _make_app(root)
    before = objective_names(app.pareto_state["objectives"])

    events: list[ConfigChanged] = []
    unsub = event_bus.subscribe(ConfigChanged, events.append)
    try:
        (root / "heartbeat.json").write_text(
            json.dumps({"objectives": "accuracy,param_count"}), encoding="utf-8"
        )
        app._poll()
    finally:
        unsub()

    assert events, "ConfigChanged published on heartbeat change"
    assert events[-1].objectives == ("accuracy", "param_count")
    after = objective_names(app.pareto_state["objectives"])
    assert after == ("accuracy", "param_count"), (before, after)
    # Panel data was invalidated and the replacement snapshot carries the
    # new objectives (recompute happens on the handler's re-render).
    assert app._snapshot is not None
    assert objective_names(app._snapshot.objectives) == ("accuracy", "param_count")


def test_config_hot_reload_invalid_campaign_keeps_current(tmp_path: Path) -> None:
    """X5: epoch_time_s (not an Objective) must not crash or clobber state."""
    root = tmp_path / "bad_cfg_root"
    seed_campaign_root(root)
    app = _make_app(root)
    before = app.pareto_state["objectives"]

    (root / "campaign.yaml").write_text(
        "hpo:\n  objectives: [accuracy, epoch_time_s]\n", encoding="utf-8"
    )
    app._poll()
    assert app.pareto_state["objectives"] == before
