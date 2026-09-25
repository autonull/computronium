"""Forensics story — first measured cell's drawer standalone."""

from __future__ import annotations

from typing import TYPE_CHECKING

from computronium.ui.adapters import adapt_cell_forensics
from computronium.ui.components.cell_forensics import CellForensicsPanel
from computronium.ui.stories.gallery import Story, register_story

if TYPE_CHECKING:
    from pathlib import Path

    from computronium.visualization.live_atlas import DashboardSnapshot


def _first_cell_key(root: Path) -> str | None:
    from computronium.visualization.live_atlas import _measured_cells

    rows = _measured_cells(root)
    if not rows:
        return None
    return max(rows, key=lambda row: row.accuracy).key


def load(snapshot: DashboardSnapshot, root: Path) -> object:
    key = _first_cell_key(root)
    if key is None:
        return None
    return adapt_cell_forensics(snapshot, root, key)


register_story(
    Story(
        key="forensics",
        title="Atlas — cell forensics",
        make_panel=CellForensicsPanel,
        load=load,
    )
)
