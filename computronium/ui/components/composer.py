"""Composer component — recipes-first build view with DialComposer."""

from __future__ import annotations

from dataclasses import dataclass, field

from nicegui import ui

from computronium.analysis.recipe_cards import RECIPE_CARDS, RecipeCard
from computronium.ui.components.workshop import (
    DialComposer,
    RecipeCardPanel,
)
from computronium.ui.design_tokens import ICONS
from computronium.ui.mode_toggle import BasePanel, tr


def _default_recipes() -> list[tuple[str, str, RecipeCard]]:
    """All measurement-backed recipe cards (family, update, card)."""
    return [(family, update, recipe) for (family, update), recipe in RECIPE_CARDS.items()]


@dataclass(frozen=True, slots=True)
class ComposerData:
    """Data for Composer panel."""

    recipes: list[tuple[str, str, RecipeCard]] = field(default_factory=_default_recipes)
    campaigns: dict[str, str] = field(default_factory=dict)  # root → name
    valid_config: bool = False
    validation_message: str = ""


class Composer(BasePanel):
    """Composer panel: recipes-first cold start, then DialComposer with
    live SystemConfig.validate() feedback. Submit copies a runnable
    ``comp campaign run`` command for the selected campaign."""

    def __init__(
        self,
        *,
        data: ComposerData | None = None,
    ) -> None:
        super().__init__(
            panel_key="composer",
            plain_explanation=(
                "The Composer is where you build learning systems. Start with a "
                "proven configuration, or compose your own from the 6-axis menu "
                "with live compatibility checking."
            ),
            why_explanation=(
                "Configuration cards show measurement-backed results from the "
                "I(C,U) analysis. The DialComposer lets you explore the full "
                "S×G×D×M×C×U space with SystemConfig.validate() ensuring "
                "only valid combinations are buildable."
            ),
            expert_explanation=(
                "Configurations from computronium.analysis.recipe_cards (M3). "
                "DialComposer uses config factories from workshop.py. "
                "Validation = SystemConfig.validate() cross-axis constraints. "
                "Submit = copy `comp campaign run --root ROOT`."
            ),
            docs_url="https://computronium.readthedocs.io/en/latest/dashboard/composer.html",
        )
        self.data = data or ComposerData()
        self._dial_composer = DialComposer()
        self._recipe_panel = RecipeCardPanel()
        self._show_dial = False
        self._selected_campaign: str | None = None

    def render(self) -> ui.element:
        """Render the Composer panel."""
        with ui.column().classes("w-full gap-4") as panel:
            self.render_header("composer")

            # Recipes-first: show recipe cards by default
            if not self._show_dial:
                self._render_recipe_cards()
            else:
                self._dial_composer.render()

            # Toggle between recipes and dial composer
            with ui.row().classes("w-full items-center justify-between mt-4"):
                ui.label().classes("flex-1")
                ui.button(
                    tr("dial_composer") if not self._show_dial else tr("recipe_card"),
                    icon=ICONS.get("tune", "tune")
                    if not self._show_dial
                    else ICONS.get("book", "menu_book"),
                    on_click=self._toggle_view,
                ).props("flat dense")

            # Submit section (shown when dial has valid config)
            self._render_submit_section()

        return panel

    def _toggle_view(self) -> None:
        """Toggle between recipe cards and dial composer."""
        self._show_dial = not self._show_dial
        # Parent will re-render on data change

    def _render_recipe_cards(self) -> None:
        """Render the recipe card gallery."""
        with ui.card().classes("w-full"):
            ui.label("Proven Recipes").classes("text-h6 mb-4")
            ui.label(
                "Start with a measurement-backed recipe. Each card shows "
                "the verdict from the I(C,U) ladder."
            ).classes("text-body text-grey mb-4")

            with ui.row().classes("w-full flex-wrap gap-4"):
                for family, update, recipe in self.data.recipes:
                    self._render_recipe_card(family, update, recipe)

            # "Start from scratch" button
            ui.separator().classes("my-4")
            ui.button(
                "Start from Scratch",
                icon=ICONS.get("add", "add"),
                on_click=self._toggle_view,
            ).props("color=primary")

    def _render_recipe_card(self, family: str, update: str, recipe: RecipeCard) -> None:
        """Render a single recipe card with select action."""
        status_colors = {
            "rescue": "positive",
            "rescue_sharp": "positive",
            "home": "primary",
            "harm": "negative",
            "closed": "grey",
            "boundary": "warning",
            "peak_collapse": "warning",
            "depth_wall_d2": "warning",
        }
        color = status_colors.get(recipe.status, "grey")

        with ui.card().classes("w-72").props("flat"):
            ui.label(f"{family} × {update}").classes("text-bold")
            ui.badge(recipe.status.replace("_", " ").title(), color=color).classes(
                "mb-2"
            )

            if recipe.parity is not None:
                ui.label(f"BP Parity: {recipe.parity:.1%}").classes("text-sm")
            if recipe.delta is not None:
                delta_color = "text-positive" if recipe.delta > 0 else "text-negative"
                ui.label(f"Δ vs BP: {recipe.delta:+.2f}").classes(
                    f"text-sm {delta_color}"
                )
            if recipe.mechanism:
                ui.label(f"Mechanism: {recipe.mechanism}").classes(
                    "text-caption text-grey"
                )
            if recipe.geometries:
                ui.label(f"Geometries: {', '.join(recipe.geometries)}").classes(
                    "text-caption text-grey"
                )
            if recipe.edge:
                ui.label(f"Edge: {recipe.edge}").classes("text-caption text-grey")

            ui.button(
                "Use This Recipe",
                icon=ICONS.get("arrow_forward", "arrow_forward"),
                on_click=lambda _, f=family, u=update: self._select_recipe(f, u),
            ).props("flat dense size=sm color=primary").classes("mt-2 w-full")

    def _select_recipe(self, family: str, update: str) -> None:
        """Pre-fill dial composer with recipe selection."""
        # Map recipe family/update to dial selections
        # This would need a mapping from recipe cards to axis options
        ui.notify(
            f"Selected {family} × {update} — switching to Dial Composer", type="info"
        )
        self._show_dial = True
        # Parent will re-render

    def _render_submit_section(self) -> None:
        """Render the submit-to-campaign section (copy runnable command)."""
        if not self._dial_composer._status_label:
            return

        # Check if current config is valid
        try:
            config = self._dial_composer._build_config()
            config.validate()
            is_valid = True
            msg = "Valid configuration — ready to submit"
        except ValueError as e:
            is_valid = False
            msg = str(e)
        except Exception:
            is_valid = False
            msg = "Validation error"

        with ui.card().classes("w-full mt-4").props("flat bordered"):
            ui.label("Submit to Campaign").classes("text-h6 mb-4")

            with ui.row().classes("w-full items-center gap-4 flex-wrap"):
                ui.select(
                    options=self.data.campaigns,
                    label="Target Campaign",
                    value=next(iter(self.data.campaigns), None),
                    on_change=lambda e: self._select_campaign(str(e.value)),
                ).props("dense outlined").classes("w-64")

                if is_valid:
                    cmd = self._command_for(self._selected_campaign)
                    ui.button(
                        "Copy Command",
                        icon="content_copy",
                        on_click=lambda _, c=cmd: ui.clipboard.write(c),
                    ).props("flat dense color=primary").tooltip(
                        "Copy the comp command that runs this configuration"
                    )

                ui.label(msg).classes(
                    "text-sm " + ("text-positive" if is_valid else "text-negative")
                )

    def _select_campaign(self, root: str) -> None:
        """Remember the campaign the command will target."""
        self._selected_campaign = root

    def _command_for(self, root: str | None) -> str:
        """Runnable command for the current configuration."""
        target = root or "artifacts/broad_map"
        return f"comp campaign run --root {target}"

    def update_data(self, data: ComposerData | None = None) -> None:
        """Update panel data."""
        if data is not None:
            self.data = data

    def set_lens(self, lens: str) -> None:
        """Set active lens (Composer has no lenses)."""


__all__ = ["Composer", "ComposerData"]
