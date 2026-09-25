"""Component story gallery (GAME.todo7 §5.2) — visual dev, zero test machinery.

One module per panel, rendered standalone against a real campaign root::

    uv run python -m computronium.ui.stories --root artifacts/broad_map --port 8099

Each story pairs a panel factory with a pure ``load`` function that derives
the panel's data from a ``DashboardSnapshot`` via the same adapters the live
dashboard uses. Omit ``--root`` to serve the synthetic fixture.
"""

from __future__ import annotations

import argparse
import tempfile
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from computronium.visualization.live_atlas import (
    EmbedCache,
    _objectives_from_heartbeat,
    render_snapshot,
    resolve_log_path,
)

if TYPE_CHECKING:
    from computronium.ui.panels import BasePanel
    from computronium.visualization.live_atlas import DashboardSnapshot

type LoadFn = Callable[[DashboardSnapshot, Path], object]


@dataclass(frozen=True, slots=True)
class Story:
    """One panel rendered standalone with real data."""

    key: str
    title: str
    make_panel: Callable[[], BasePanel]
    load: LoadFn


STORIES: dict[str, Story] = {}


def register_story(entry: Story) -> Story:
    """Register a story (called once per story module)."""
    STORIES[entry.key] = entry
    return entry


def _ensure_registered() -> None:
    from computronium.ui.stories import (
        atlas,
        budget,
        defects,
        evidence,
        forensics,
        monitor,
    )

    _ = (atlas, budget, defects, evidence, forensics, monitor)


def build_story(key: str, root: Path) -> tuple[BasePanel, object]:
    """Build a panel plus its data from a real campaign root (no daemon)."""
    _ensure_registered()
    entry = STORIES[key]
    snapshot = render_snapshot(
        root,
        resolve_log_path(root, None),
        EmbedCache(),
        objectives=_objectives_from_heartbeat(root),
        with_atlas=False,
    )
    panel = entry.make_panel()
    return panel, entry.load(snapshot, root)


def serve(root: Path | None = None, port: int = 8099) -> None:
    """Serve every story on its own page for hot-reload visual development."""
    from nicegui import ui

    _ensure_registered()
    target = root or _demo_root()

    @ui.page("/")
    def _index() -> None:
        with ui.column().classes("gap-2 p-4"):
            ui.label("Story gallery").classes("text-h4")
            for entry_key in sorted(STORIES):
                ui.link(STORIES[entry_key].title, f"/story/{entry_key}")

    for entry_key in sorted(STORIES):

        @ui.page(f"/story/{entry_key}")
        def _story_page(key: str = entry_key) -> None:
            panel, data = build_story(key, target)
            panel.update_data(data)
            panel.render()

    ui.run(title="Computronium stories", port=port, reload=True)


def _demo_root() -> Path:
    from tests.ui.fixture import seed_campaign_root

    root = Path(tempfile.mkdtemp(prefix="story_")) / "broad_map"
    seed_campaign_root(root)
    return root


def main() -> int:
    parser = argparse.ArgumentParser(prog="computronium.ui.stories")
    parser.add_argument("--root", type=Path, default=None)
    parser.add_argument("--port", type=int, default=8099)
    args = parser.parse_args()
    serve(args.root, args.port)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
