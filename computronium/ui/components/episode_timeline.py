"""Episode Timeline component (M1.14) — sleep/wake boundaries from campaign event log."""

from __future__ import annotations

from dataclasses import dataclass

from nicegui import ui

from computronium.ui.design_tokens import ICONS
from computronium.ui.mode_toggle import BasePanel


@dataclass(frozen=True, slots=True)
class EpisodeEvent:
    """An event in the episode timeline."""

    episode: int
    timestamp: float
    event_type: (
        str  # "sleep" | "wake" | "consolidation" | "genome_change" | "probe_batch"
    )
    detail: str
    genome_before: str | None = None
    genome_after: str | None = None


class EpisodeTimeline(BasePanel):
    """Episode Timeline: visualize sleep/wake boundaries and consolidation events."""

    EVENT_ICONS = {
        "sleep": "🌙",
        "wake": "🌅",
        "consolidation": "🔄",
        "genome_change": "🧬",
        "probe_batch": "🔬",
    }
    EVENT_LABELS = {
        "sleep": "Sleep",
        "wake": "Wake",
        "consolidation": "Consolidation",
        "genome_change": "Genome Change",
        "probe_batch": "Probe Batch",
    }

    def __init__(
        self,
        *,
        events: list[EpisodeEvent] | None = None,
        current_episode: int = 0,
    ) -> None:
        super().__init__(
            panel_key="episode_timeline",
            plain_explanation=(
                "This timeline shows the sleep/wake cycles of the campaign. "
                "Consolidation happens during sleep. Genome changes only at boundaries."
            ),
            why_explanation=(
                "The campaign alternates between training (wake) and consolidation (sleep). "
                "This makes the evolutionary architecture visible: morphology only at boundaries."
            ),
            expert_explanation=(
                "From campaign event log. Episode boundaries = sleep/wake transitions. "
                "Consolidation events = plastic state crystallization. "
                "Genome changes only at boundaries (never mid-pass). "
                "Probe batches fire during stagnation. "
                "Current episode highlighted."
            ),
            docs_url="https://computronium.readthedocs.io/en/latest/dashboard/episodes.html",
        )
        self.events = events or []
        self.current_episode = current_episode
        self._timeline_container: ui.element = ui.column().classes("w-full")

    def render(self) -> ui.element:
        """Render the Episode Timeline."""
        with ui.column().classes("w-full gap-4") as panel:
            self.render_header("episode_timeline")

            # Current episode indicator
            with ui.row().classes("w-full items-center gap-2"):
                ui.icon(ICONS["episode"]).classes("text-xl")
                ui.label(
                    f"{self.tr('current_episode')}: {self.current_episode}"
                ).classes("text-h6")
                ui.separator().classes("flex-1")
                ui.label(self.tr("morphology_at_boundaries")).classes(
                    "text-caption text-grey"
                )

            # Timeline
            self._timeline_container = ui.column().classes("w-full")
            with self._timeline_container:
                self._render_timeline()

        return panel

    def _render_timeline(self) -> None:
        """Render the episode timeline."""
        self._timeline_container.clear()
        with self._timeline_container:
            if not self.events:
                ui.label(self.tr("no_episode_data")).classes(
                    "text-grey text-center p-8"
                )
                return

            # Group by episode
            from collections import defaultdict

            by_episode = defaultdict(list)
            for event in self.events:
                by_episode[event.episode].append(event)

            for episode in sorted(by_episode.keys(), reverse=True):
                ep_events = by_episode[episode]
                is_current = episode == self.current_episode

                with ui.card().classes("w-full").props("flat bordered"):
                    # Episode header
                    with ui.row().classes("w-full items-center justify-between"):
                        with ui.row().classes("items-center gap-2"):
                            if is_current:
                                ui.badge(self.tr("current"), color="primary").classes(
                                    "text-xs"
                                )
                            ui.label(f"{self.tr('episode')} {episode}").classes(
                                "text-bold"
                            )

                        # Episode duration
                        if len(ep_events) >= 2:
                            duration = ep_events[-1].timestamp - ep_events[0].timestamp
                            ui.label(f"{duration:.1f}s").classes(
                                "text-sm text-grey font-mono"
                            )

                    # Events in this episode
                    for event in ep_events:
                        icon = self.EVENT_ICONS.get(event.event_type, "📋")
                        label = self.EVENT_LABELS.get(
                            event.event_type, event.event_type
                        )
                        time_str = self._format_time(event.timestamp)

                        with ui.row().classes("w-full items-center gap-2 pl-4 py-1"):
                            ui.label(time_str).classes(
                                "font-mono text-xs text-grey w-16"
                            )
                            ui.label(icon).classes("text-base")
                            ui.label(label).classes("text-sm text-grey")
                            ui.label(event.detail).classes("text-sm font-mono flex-1")

                            if event.genome_before and event.genome_after:
                                ui.label(
                                    f"{event.genome_before[:16]} → {event.genome_after[:16]}"
                                ).classes("text-xs text-primary font-mono")

    def _format_time(self, timestamp: float) -> str:
        """Format timestamp as HH:MM:SS."""
        import time

        return time.strftime("%H:%M:%S", time.localtime(timestamp))

    def update_data(
        self,
        *,
        events: list[EpisodeEvent] | None = None,
        current_episode: int | None = None,
    ) -> None:
        """Update timeline data."""
        if events is not None:
            self.events = events
        if current_episode is not None:
            self.current_episode = current_episode
        self._render_timeline()

    def _refresh(self) -> None:
        """Refresh on mode change."""
        self._render_timeline()
