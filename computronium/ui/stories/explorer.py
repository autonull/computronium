"""Objective-explorer story — parallel coordinates standalone."""

from __future__ import annotations

from typing import TYPE_CHECKING

from computronium.ui.adapters import adapt_objective_explorer
from computronium.ui.components.objective_explorer import ObjectiveExplorerPanel
from computronium.ui.stories.gallery import Story, register_story

if TYPE_CHECKING:
    from pathlib import Path

    from computronium.visualization.live_atlas import DashboardSnapshot


def load(snapshot: DashboardSnapshot, root: Path) -> object:
    return adapt_objective_explorer(snapshot, root)


register_story(
    Story(
        key="explorer",
        title="Atlas — objective explorer",
        make_panel=ObjectiveExplorerPanel,
        load=load,
    )
)
