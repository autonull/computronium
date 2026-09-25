"""Evidence story — beliefs and experiments standalone."""

from __future__ import annotations

from typing import TYPE_CHECKING

from computronium.ui.adapters import adapt_evidence
from computronium.ui.components.evidence_panel import EvidencePanel
from computronium.ui.stories.gallery import Story, register_story

if TYPE_CHECKING:
    from pathlib import Path

    from computronium.visualization.live_atlas import DashboardSnapshot


def load(snapshot: DashboardSnapshot, root: Path) -> object:
    return adapt_evidence(snapshot, root)


register_story(
    Story(
        key="evidence",
        title="Evidence — beliefs & claims",
        make_panel=EvidencePanel,
        load=load,
    )
)
