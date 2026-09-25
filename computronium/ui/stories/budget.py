"""Budget story — burn-down standalone."""

from __future__ import annotations

from typing import TYPE_CHECKING

from computronium.ui.adapters import adapt_budget
from computronium.ui.components.budget_panel import BudgetPanel
from computronium.ui.stories.gallery import Story, register_story

if TYPE_CHECKING:
    from pathlib import Path

    from computronium.visualization.live_atlas import DashboardSnapshot


def load(snapshot: DashboardSnapshot, root: Path) -> object:
    return adapt_budget(snapshot, root)


register_story(
    Story(key="budget", title="Monitor — budget", make_panel=BudgetPanel, load=load)
)
