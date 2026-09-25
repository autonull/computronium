"""Scrubber story — burst-log scrubber standalone."""

from __future__ import annotations

from typing import TYPE_CHECKING

from computronium.ui.adapters import adapt_scrubber
from computronium.ui.components.scrubber import ScrubberPanel
from computronium.ui.stories.gallery import Story, register_story

if TYPE_CHECKING:
    from pathlib import Path

    from computronium.visualization.live_atlas import DashboardSnapshot


def load(snapshot: DashboardSnapshot, root: Path) -> object:
    return adapt_scrubber(snapshot, root)


register_story(
    Story(
        key="scrubber",
        title="Monitor — scrubber",
        make_panel=ScrubberPanel,
        load=load,
    )
)
