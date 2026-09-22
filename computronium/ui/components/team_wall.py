"""Team Wall (M3.3) — cooperative team wall, opt-in per team."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from nicegui import ui

from computronium.ui.design_tokens import ICONS
from computronium.ui.mode_toggle import BasePanel

if TYPE_CHECKING:
    from collections.abc import Callable


@dataclass(frozen=True, slots=True)
class TeamMember:
    """A team member on the wall."""

    user_id: str
    name: str
    avatar: str | None = None


@dataclass(frozen=True, slots=True)
class TeamProgress:
    """Cooperative team progress."""

    team_id: str
    team_name: str
    members: list[TeamMember]
    regions_charted: int = 0
    defects_fixed: int = 0
    quests_completed: int = 0
    badges_earned: int = 0
    personal_bests: int = 0


class TeamWall(BasePanel):
    """Team Wall: cooperative progress display, opt-in per team.

    No individual leaderboards. Team progress = cooperative totals only.
    """

    def __init__(
        self,
        team: TeamProgress | None = None,
        on_join_team: Callable[[], None] | None = None,
        on_create_team: Callable[[], None] | None = None,
    ) -> None:
        super().__init__(
            panel_key="team_wall",
            plain_explanation=(
                "Work together with your team. This wall shows your team's "
                "combined progress: regions charted, defects fixed, quests "
                "completed. No individual rankings — just shared progress."
            ),
            why_explanation=(
                "Research is collaborative. The team wall shows what your "
                "group has achieved together, without pitting individuals "
                "against each other. Opt-in only — you choose to join."
            ),
            expert_explanation=(
                "Team progress aggregates cooperative metrics only: "
                "sum of regions_charted, defects_fixed, quests_completed, "
                "badges_earned, personal_bests across all team members. "
                "No individual leaderboards, no competitive rankings. "
                "Per GAME.md M3.3: 'Team progress = cooperative totals only.'"
            ),
            docs_url="https://computronium.readthedocs.io/en/latest/dashboard/teams.html",
        )
        self.team = team
        self.on_join_team = on_join_team
        self.on_create_team = on_create_team
        self._joined = team is not None

    def set_team(self, team: TeamProgress) -> None:
        """Set the current team."""
        self.team = team
        self._joined = True
        self._refresh()

    def render(self) -> ui.element:
        """Render the team wall."""
        with ui.column().classes("w-full gap-4") as panel:
            self.render_header("team_wall")

            if not self._joined:
                self._render_join_prompt()
            elif self.team:
                self._render_team()
            else:
                ui.label("No team data available").classes("text-grey")

        return panel

    def _render_join_prompt(self) -> None:
        """Render prompt to join or create a team."""
        with ui.card().classes("w-full").props("flat bordered"):
            ui.icon(ICONS["badge"]).classes("text-4xl text-primary")
            ui.label("Join a team").classes("text-h5 mt-2")
            ui.label(
                "Team walls show cooperative progress — no individual "
                "leaderboards. Opt in to share your progress with colleagues."
            ).classes("text-body text-grey mb-4")

            with ui.row().classes("w-full gap-2"):
                ui.button(
                    "Join Existing Team",
                    icon="group_add",
                    on_click=self._open_join_dialog,
                ).props("color=primary")

                ui.button(
                    "Create New Team",
                    icon="add_circle",
                    on_click=self._open_create_dialog,
                ).props("flat color=primary")

    def _open_join_dialog(self) -> None:
        """Open dialog to join a team."""
        with ui.dialog() as dialog, ui.card().classes("w-[500px] p-6"):
            ui.label("Join a Team").classes("text-h6 mb-4")
            ui.input("Team ID or Invite Code", placeholder="Enter team ID").props(
                "dense outlined"
            ).classes("w-full mb-4")

            with ui.row().classes("w-full justify-end gap-2"):
                ui.button("Cancel", on_click=dialog.close).props("flat")
                ui.button(
                    "Join",
                    on_click=lambda: (dialog.close(), self._join_team()),
                    color="primary",
                )

        dialog.open()

    def _open_create_dialog(self) -> None:
        """Open dialog to create a team."""
        with ui.dialog() as dialog, ui.card().classes("w-[500px] p-6"):
            ui.label("Create a Team").classes("text-h6 mb-4")
            ui.input("Team Name", placeholder="My Research Team").props(
                "dense outlined"
            ).classes("w-full mb-4")

            with ui.row().classes("w-full justify-end gap-2"):
                ui.button("Cancel", on_click=dialog.close).props("flat")
                ui.button(
                    "Create",
                    on_click=lambda: (dialog.close(), self._create_team()),
                    color="primary",
                )

        dialog.open()

    def _join_team(self) -> None:
        """Handle joining a team."""
        if self.on_join_team:
            self.on_join_team()

    def _create_team(self) -> None:
        """Handle creating a team."""
        if self.on_create_team:
            self.on_create_team()

    def _render_team(self) -> None:
        """Render the team progress."""
        if not self.team:
            return

        # Team header
        with ui.card().classes("w-full").props("flat bordered"):
            with ui.row().classes("w-full items-center gap-4"):
                ui.icon(ICONS["badge"]).classes("text-3xl text-primary")
                with ui.column().classes("flex-1"):
                    ui.label(self.team.team_name).classes("text-h5")
                    ui.label(f"Team ID: {self.team.team_id}").classes(
                        "text-caption text-grey"
                    )
                    ui.label(f"{len(self.team.members)} members").classes(
                        "text-caption text-grey"
                    )

        # Cooperative progress metrics
        ui.label("Cooperative Progress").classes("text-h6")
        with ui.row().classes("w-full gap-4 flex-wrap"):
            self._metric_card(
                "Regions Charted", self.team.regions_charted, ICONS["region"]
            )
            self._metric_card("Defects Fixed", self.team.defects_fixed, ICONS["repair"])
            self._metric_card(
                "Quests Completed", self.team.quests_completed, ICONS["quest"]
            )
            self._metric_card("Badges Earned", self.team.badges_earned, ICONS["badge"])
            self._metric_card(
                "Personal Bests", self.team.personal_bests, ICONS["record"]
            )

        # Team members
        ui.label("Team Members").classes("text-h6 mt-4")
        with ui.row().classes("w-full gap-4 flex-wrap"):
            for member in self.team.members:
                with ui.card().classes("min-w-[150px]").props("flat bordered"):
                    if member.avatar:
                        ui.avatar(member.avatar).classes("text-2xl")
                    else:
                        ui.icon(ICONS["map"]).classes("text-3xl text-primary")
                    ui.label(member.name).classes("text-body text-center")

    def _metric_card(self, label: str, value: int, icon: str) -> ui.element:
        """Render a metric card."""
        with ui.card().classes("flex-1 min-w-[150px]").props("flat bordered") as card:
            ui.icon(icon).classes("text-2xl text-primary")
            ui.label(str(value)).classes("text-h4 text-bold")
            ui.label(label).classes("text-caption text-grey")
        return card

    def _refresh(self) -> None:
        """Refresh on mode change."""


def create_team_wall(
    team: TeamProgress | None = None,
) -> TeamWall:
    """Create the team wall component."""
    return TeamWall(team=team)
