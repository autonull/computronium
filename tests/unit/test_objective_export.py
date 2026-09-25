"""Objective explorer (§4.3) + minimal exports (§4.7) — content tests."""

from __future__ import annotations

from typing import TYPE_CHECKING

from computronium.ui.adapters import _decimate_stride, adapt_objective_explorer
from computronium.ui.components.objective_explorer import build_parcoords_figure
from computronium.ui.data_adapters import AdapterContext
from computronium.ui.exports import explorer_csv, figure_html
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


def test_explorer_content(tmp_path: Path) -> None:
    root = tmp_path / "broad_map"
    seed_campaign_root(root)
    data = adapt_objective_explorer(_context(root).snapshot, root)
    assert len(data.cell_keys) == 4
    assert all(len(key.split("|")) == 4 for key in data.cell_keys)
    assert "accuracy" in data.axes
    assert len(data.columns) == len(data.axes)
    assert all(len(column) == 4 for column in data.columns)
    assert len(data.pareto_mask) == 4
    assert not data.decimated
    accuracy = data.columns[data.axes.index("accuracy")]
    assert max(accuracy) == 0.83


def test_explorer_empty_root(tmp_path: Path) -> None:
    root = tmp_path / "broad_map"
    root.mkdir(parents=True)
    data = adapt_objective_explorer(_context(root).snapshot, root)
    assert data.cell_keys == () and data.pareto_mask == ()


def test_decimate_stride() -> None:
    assert _decimate_stride(4) == 1
    assert _decimate_stride(2000) == 1
    assert _decimate_stride(2001) == 2
    assert 2001 // _decimate_stride(5000) <= 2000


def test_figure_traces(tmp_path: Path) -> None:
    root = tmp_path / "broad_map"
    seed_campaign_root(root)
    data = adapt_objective_explorer(_context(root).snapshot, root)
    fig = build_parcoords_figure(data, ("accuracy", "walltime_s"))
    payload = fig.to_dict()
    assert len(payload["data"]) >= 1
    dims = payload["data"][0]["dimensions"]
    assert [dim["label"] for dim in dims] == ["accuracy", "walltime_s"]
    assert len(dims[0]["values"]) == 4


def test_exports_bytes(tmp_path: Path) -> None:
    root = tmp_path / "broad_map"
    seed_campaign_root(root)
    data = adapt_objective_explorer(_context(root).snapshot, root)
    raw = explorer_csv(data).decode("utf-8")
    lines = raw.strip().splitlines()
    assert lines[0].startswith("cell_key,accuracy,")
    assert len(lines) == 5
    html = figure_html(build_parcoords_figure(data, ("accuracy",)))
    assert b"plotly" in html.lower()
