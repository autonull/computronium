"""Monitor story — health tiles standalone."""

from __future__ import annotations

from typing import TYPE_CHECKING

from computronium.ui.adapters import adapt_health_panel
from computronium.ui.components.monitor import MonitorData, MonitorView, SessionDelta
from computronium.ui.stories.gallery import Story, register_story
from computronium.visualization.live_atlas import liveness

if TYPE_CHECKING:
    from pathlib import Path

    from computronium.visualization.live_atlas import DashboardSnapshot


def load(snapshot: DashboardSnapshot, root: Path) -> MonitorData:
    return MonitorData(
        liveness=liveness(root, False),
        tiles=adapt_health_panel(snapshot, root),
        loss_history=[],
        feed=[],
        intent=None,
        session_delta=SessionDelta(),
        ticker=snapshot.ticker,
        layout_note=snapshot.layout_note,
    )


register_story(
    Story(
        key="monitor", title="Monitor — health tiles", make_panel=MonitorView, load=load
    )
)
