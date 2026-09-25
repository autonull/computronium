"""Defects story — repair bench standalone."""

from __future__ import annotations

from typing import TYPE_CHECKING

from computronium.ui.adapters import RepairBenchData, adapt_repair_bench
from computronium.ui.components import RepairBench
from computronium.ui.stories.gallery import Story, register_story

if TYPE_CHECKING:
    from pathlib import Path

    from computronium.visualization.live_atlas import DashboardSnapshot


def load(snapshot: DashboardSnapshot, root: Path) -> RepairBenchData:
    return adapt_repair_bench(snapshot, root)


register_story(
    Story(
        key="defects", title="Defects — repair bench", make_panel=RepairBench, load=load
    )
)
