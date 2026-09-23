"""D3 rebuild flag + X4 multi-root + X5 config hot-reload (behavioral, headless)."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from computronium.ui.dashboard import DashboardApp
from computronium.ui.event_bus import ConfigChanged, event_bus
from computronium.ui.recognition import RecognitionEvent
from computronium.ui.recognition.state_store import RecognitionStateStore
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
        "gamify": True,
        "ui_actions": False,
        "rebuild_state": False,
    }
    params.update(kwargs)
    app = DashboardApp(**params)  # type: ignore[arg-type]
    app.build()
    return app


def test_rebuild_flag_persists_and_round_trips(tmp_path: Path) -> None:
    """D3: --rebuild-ui-state persists the fold; progress panel round-trips."""
    from computronium.ui.components.progress_panel import ProgressPanel

    root = tmp_path / "rebuild_root"
    seed_campaign_root(root)

    store = RecognitionStateStore(db_path=root / "ui_state.sqlite")
    store.append_event(
        RecognitionEvent("pareto_front_expanded", 1.0, {"cell_key": "a|b|c|d"})
    )
    store.append_event(RecognitionEvent("measurement_recorded", 2.0, {"is_void": True}))
    store.append_event(RecognitionEvent("cell_completed", 3.0, {"cell_key": "x|y|z|w"}))

    app = _make_app(root, rebuild_state=True)
    assert store.get_last_rebuild_at() is not None, "persist_state must record rebuild"

    state = store.rebuild_from_events()
    badge_ids = {badge.id for badge in state.badges}
    assert "gold_standard" in badge_ids, badge_ids
    assert "honest_broker" in badge_ids, badge_ids

    data = app._get_panel_data("progress")
    assert data is not None and data.badges, "progress adapter yields badges"
    assert data.quests, "progress adapter yields quest specs"

    app.current_panel = "progress"
    app._render_current_panel()
    panel = app._panel_as("progress", ProgressPanel)
    assert panel is not None and panel.data.badges, "panel update_data round-trip"


def test_multi_root_switch_resets_state(tmp_path: Path) -> None:
    """X4: switch_root swaps caches/panels/signature per root."""
    from computronium.visualization.live_atlas import watch_signature

    root_a = tmp_path / "root_a"
    root_b = tmp_path / "root_b"
    seed_campaign_root(root_a)
    seed_campaign_root(root_b)

    app = _make_app(root_a, roots=(root_a, root_b))
    app._switch_panel("health")
    assert "health" in app._panels
    old_health = app._panels["health"]

    app.switch_root(root_b)
    assert app.root == root_b
    # Per-root reset: old instances discarded; the re-render lazily builds a
    # fresh panel bound to root_b.
    assert app._panels.get("health") is not old_health, "panel instances are per-root"
    assert app.current_panel == "health"
    assert app.last_signature == watch_signature(root_b)
    assert app.log_path is not None and root_b in app.log_path.parents
    assert app.recognition_store is not None
    assert app.recognition_store._db_path == root_b / "ui_state.sqlite"  # type: ignore[attr-defined]

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
