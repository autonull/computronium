"""Preview Shelf (M3.6) — Auto-Evolve entry with falsification plan."""

from __future__ import annotations

from dataclasses import dataclass

from nicegui import ui

from computronium.ui.design_tokens import ICONS
from computronium.ui.mode_toggle import BasePanel


@dataclass(frozen=True, slots=True)
class PreviewEntry:
    """One entry on the preview shelf."""

    key: str
    title: str
    proposal: str
    status: str
    falsification_plan: str
    docs_url: str | None = None


class PreviewShelf(BasePanel):
    """Preview Shelf: shows proposed but unimplemented features.

    Each entry is clearly labeled "Proposed — not implemented" with a
    falsification plan in plain language. No live UI, no metrics, no creatures.
    """

    def __init__(self, entries: list[PreviewEntry] | None = None) -> None:
        super().__init__(
            panel_key="preview_shelf",
            plain_explanation=(
                "This shelf shows features that are proposed but not yet built. "
                "Each entry explains what it would do and how we'd prove it wrong. "
                "Nothing here is live — it's a preview of future work."
            ),
            why_explanation=(
                "Honest preview prevents hype. The falsification plan is the "
                "most important part: if we can't say how to prove it wrong, "
                "we shouldn't build it."
            ),
            expert_explanation=(
                "Auto-Evolve is a constitutional self-modification engine: "
                "asexual mutation (neutral birth) + slope-based selection + "
                "immutable Constitution. Per AUTOTILE.md §8.5 kill criterion: "
                "if probe-scale E1–E4 don't validate by M3, Auto-Evolve is "
                "removed from the roadmap. This shelf implements the Preview "
                "Shelf pattern from GAME.md §5.9/§11."
            ),
            docs_url="https://computronium.readthedocs.io/en/latest/auto-evolve.html",
        )
        self.entries = entries or self._default_entries()

    def _default_entries(self) -> list[PreviewEntry]:
        """Default Auto-Evolve entry per GAME.md M3.6."""
        return [
            PreviewEntry(
                key="auto_evolve",
                title="Auto-Evolve (Constitutional Self-Modification)",
                proposal=(
                    "An evolutionary engine that grows learning mechanisms "
                    "under stability, passivity, and resource constraints. "
                    "Neutral birth (asexual mutation) + slope-based selection "
                    "(adaptation probes) + 6 invariant Constitution. "
                    "Not a game, not a simulation — a self-modifying learning "
                    "system governed by physics."
                ),
                status="Proposed — not implemented",
                falsification_plan=(
                    "Per AUTOTILE.md §8.5: if probe-scale experiments E1–E4 "
                    "(deep chaotic unfolding, Kolmogorov compression, fabric "
                    "reconfiguration, program sequencing) don't validate by M3, "
                    "Auto-Evolve is removed from the roadmap. "
                    "E1 (deep chaotic unfolding) already falsified: "
                    "composition-error compounding prevents reliable long-horizon "
                    "rollout with fixed-horizon local credit."
                ),
                docs_url="https://computronium.readthedocs.io/en/latest/auto-evolve.html",
            )
        ]

    def render(self) -> ui.element:
        """Render the Preview Shelf."""
        with ui.column().classes("w-full gap-4") as panel:
            self.render_header("preview_shelf")

            # Status badge
            with ui.row().classes("w-full items-center gap-2 mb-4"):
                ui.icon(ICONS["warning"]).classes("text-xl text-warning")
                ui.label(self.tr("proposed_not_implemented")).classes(
                    "text-h6 text-warning font-bold"
                )

            for entry in self.entries:
                self._render_entry(entry)

        return panel

    def _render_entry(self, entry: PreviewEntry) -> None:
        """Render a single preview entry."""
        with (
            ui.card().classes("w-full").props("flat bordered"),
            ui.row().classes("w-full items-start gap-4"),
        ):
            ui.icon(ICONS["preview"]).classes("text-3xl text-primary shrink-0")

            with ui.column().classes("flex-1 gap-2"):
                # Title + status
                with ui.row().classes("items-center gap-2 flex-wrap"):
                    ui.label(entry.title).classes("text-h5")
                    ui.badge(entry.status, color="warning").props("outline")

                # Proposal
                with ui.expansion("What this proposes", value=True).classes("w-full"):
                    ui.label(entry.proposal).classes("text-body")

                # Falsification plan (always visible in explorer)
                with ui.expansion("How we'd prove this wrong", value=True).classes(
                    "w-full"
                ):
                    ui.label(entry.falsification_plan).classes(
                        "text-body text-negative"
                    )

                # Docs link
                if entry.docs_url:
                    ui.separator().classes("my-2")
                    ui.link("Read the full specification", entry.docs_url).props(
                        "target=_blank"
                    ).classes("text-primary")

    def _refresh(self) -> None:
        """Refresh on mode change."""


def create_auto_evolve_preview() -> PreviewShelf:
    """Create the Preview Shelf with the Auto-Evolve entry."""
    return PreviewShelf()
