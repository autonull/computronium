"""Atlas story — discovery map standalone."""

from __future__ import annotations

from typing import TYPE_CHECKING

from computronium.ui.adapters import DiscoveryMapData, adapt_discovery_map
from computronium.ui.components import DiscoveryMap
from computronium.ui.stories.gallery import Story, register_story

if TYPE_CHECKING:
    from pathlib import Path

    from computronium.visualization.live_atlas import DashboardSnapshot


def load(snapshot: DashboardSnapshot, root: Path) -> DiscoveryMapData:
    return adapt_discovery_map(snapshot, root)


register_story(
    Story(
        key="atlas", title="Atlas — discovery map", make_panel=DiscoveryMap, load=load
    )
)
