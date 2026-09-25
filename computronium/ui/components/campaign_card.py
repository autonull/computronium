"""Campaign Card Component (M3 recommendation) — renders campaign manifests.

Displays campaign metadata from YAML: plain/technical title, description,
objectives, status, entry points. Zero dashboard code per spec.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from nicegui import ui

from computronium.ui.panels import BasePanel


@dataclass(frozen=True, slots=True)
class CampaignManifest:
    """Campaign manifest parsed from YAML."""

    name: str
    title_explorer: str
    title_lab: str
    description_explorer: str
    description_lab: str
    objectives: list[str]
    status: str
    entry_points: dict[str, str]
    metadata: dict[str, Any]


class CampaignCard(BasePanel):
    """Render a campaign manifest as a card."""

    def __init__(
        self,
        manifest_path: Path | str,
        *,
        clickable: bool = True,
    ) -> None:
        super().__init__(
            panel_key="campaign_card",
            plain="A campaign is a coordinated exploration of the 6-axis space. This card shows what the campaign is about and how to join.",
            why="Campaigns define the search space (which primitives to explore), the objectives (what to optimize), and the budget. This card makes that visible at a glance.",
            expert="Campaign YAML specifies: substrate/geometry/dynamics/plasticity/credit/update strata, objective specs with weights/margins, maturation gates (l0→l1→l2), and CEEC claim thresholds. Entry points map to comp CLI subcommands.",
            docs_url="https://github.com/computronium/computronium/blob/main/docs/platform/campaigns.md",
        )
        self._manifest = self._load_manifest(manifest_path)
        self._clickable = clickable

    def _load_manifest(self, path: Path | str) -> CampaignManifest:
        """Load and parse campaign manifest from YAML."""
        import yaml

        path = Path(path)
        if not path.exists():
            return CampaignManifest(
                name="unknown",
                title_explorer="Unknown Campaign",
                title_lab="Unknown Campaign",
                description_explorer="Manifest not found.",
                description_lab="Manifest not found.",
                objectives=[],
                status="unknown",
                entry_points={},
                metadata={},
            )

        data = yaml.safe_load(path.read_text(encoding="utf-8"))

        return CampaignManifest(
            name=data.get("name", path.stem),
            title_explorer=data.get("title_explorer", data.get("title", path.stem)),
            title_lab=data.get("title_lab", data.get("title", path.stem)),
            description_explorer=data.get(
                "description_explorer", data.get("description", "")
            ),
            description_lab=data.get("description_lab", data.get("description", "")),
            objectives=data.get("objectives", []),
            status=data.get("status", "proposed"),
            entry_points=data.get("entry_points", {}),
            metadata=data.get("metadata", {}),
        )

    def render(self) -> ui.element:
        """Render the campaign card."""
        with ui.card().classes("w-full") as card:
            # Title with status badge
            with ui.row().classes("w-full items-center justify-between mb-2"):
                ui.label(self._get_title()).classes("text-h6")
                self._render_status_badge()

            # Description
            if self._get_description():
                ui.label(self._get_description()).classes("text-body text-grey mb-4")

            # Objectives
            if self._manifest.objectives:
                ui.label("Goals").classes("text-bold text-sm mb-2")
                with ui.row().classes("w-full flex-wrap gap-2 mb-4"):
                    for obj in self._manifest.objectives:
                        ui.badge(obj, color="primary").props("outline")

            # Entry points
            if self._manifest.entry_points:
                ui.label("Entry points").classes("text-bold text-sm mb-2")
                with ui.row().classes("w-full flex-wrap gap-2"):
                    for label, command in self._manifest.entry_points.items():
                        if self._clickable:

                            def make_handler(cmd: str):
                                return lambda _: self._run_entry_point(cmd)

                            ui.button(
                                label,
                                icon="play_arrow",
                                on_click=make_handler(command),
                            ).props("flat dense size=sm")
                        else:
                            ui.label(f"{label}: {command}").classes(
                                "text-caption font-mono text-grey"
                            )

            # Metadata (collapsible)
            if self._manifest.metadata:
                with ui.expansion("Metadata", value=False).classes("w-full mt-4"):
                    for key, value in self._manifest.metadata.items():
                        with ui.row().classes("w-full items-center gap-2"):
                            ui.label(key).classes("text-bold text-sm")
                            ui.label(str(value)).classes("text-sm font-mono text-grey")

        return card

    def _get_title(self) -> str:
        """Get title in the single plain register."""
        return self._manifest.title_explorer

    def _get_description(self) -> str:
        """Get description in the single plain register."""
        return self._manifest.description_explorer

    def _render_status_badge(self) -> None:
        """Render status badge with a plain label."""
        status_colors = {
            "proposed": ("grey", "proposed"),
            "running": ("green", "running"),
            "paused": ("amber", "paused"),
            "completed": ("blue", "completed"),
            "archived": ("grey", "archived"),
        }
        color, default_label = status_colors.get(
            self._manifest.status, ("grey", "unknown")
        )
        ui.badge(default_label, color=color).props("outline")

    def _run_entry_point(self, command: str) -> None:
        """Execute an entry point command (stub for demo)."""
        ui.notify(f"Running: {command}", type="info")
        # In real implementation: subprocess.Popen(command.split())


class CampaignCardGallery:
    """Gallery of campaign cards from a directory of manifests."""

    def __init__(self, manifests_dir: Path | str) -> None:
        self._manifests_dir = Path(manifests_dir)
        self._cards: list[CampaignCard] = []
        self._load_cards()

    def _load_cards(self) -> None:
        """Load all campaign manifests from directory."""
        if not self._manifests_dir.exists():
            return
        for manifest_path in sorted(self._manifests_dir.glob("*.yaml")):
            self._cards.append(CampaignCard(manifest_path))

    def render(self) -> ui.element:
        """Render the campaign gallery as a grid."""
        with ui.column().classes("w-full gap-4") as container:
            ui.label("Campaign").classes("text-h5 mb-4")

            if not self._cards:
                ui.label("No campaigns found.").classes("text-grey")
                return container

            with ui.row().classes("w-full flex-wrap gap-4"):
                for card in self._cards:
                    with ui.column().classes("w-80"):
                        card.render()

        return container


def create_campaign_card(
    manifest_path: Path | str, *, clickable: bool = True
) -> CampaignCard:
    """Factory function for CampaignCard."""
    return CampaignCard(manifest_path, clickable=clickable)


def create_campaign_gallery(manifests_dir: Path | str) -> CampaignCardGallery:
    """Factory function for CampaignCardGallery."""
    return CampaignCardGallery(manifests_dir)


__all__ = [
    "CampaignCard",
    "CampaignCardGallery",
    "CampaignManifest",
    "create_campaign_card",
    "create_campaign_gallery",
]
