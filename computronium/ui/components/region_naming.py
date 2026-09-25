"""Region Naming (M3.2) — propose plain names for map regions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from nicegui import ui

from computronium.ui.design_tokens import ICONS
from computronium.ui.panels import BasePanel

if TYPE_CHECKING:
    from collections.abc import Callable


@dataclass(frozen=True, slots=True)
class RegionName:
    """A proposed name for a map region."""

    region_id: str
    name: str
    proposed_by: str
    timestamp: float
    version: int = 1
    reverted: bool = False


class RegionNaming(BasePanel):
    """Region Naming: propose plain names for map regions.

    Names are stored as presentation metadata only — never in measurement
    records. Versioned and revertible.
    """

    def __init__(
        self,
        regions: list[dict[str, object]] | None = None,
        on_propose: Callable[[str, str, int], None] | None = None,
    ) -> None:
        super().__init__(
            panel_key="region_naming",
            plain=(
                "Give plain-language names to regions on the map. This helps "
                "you remember what you've explored. Names are just labels — "
                "they don't affect any measurements."
            ),
            why=(
                "Technical coordinates like 'EnergyMinimization × "
                "ThermodynamicContrast × EuclideanUpdate' are precise but hard "
                "to remember. Plain names like 'Valley of Stable EqProp' make "
                "the map navigable for everyone."
            ),
            expert=(
                "Region names are stored as presentation metadata in the KB, "
                "versioned and revertible. They never appear in measurement "
                "records, CEEC ledger, or promotion logic. Per GAME.md M3.2: "
                "'Names stored as presentation metadata, never in measurement "
                "records.'"
            ),
            docs_url="https://computronium.readthedocs.io/en/latest/dashboard/regions.html",
        )
        self.regions = regions or []
        self.on_propose = on_propose
        self._names: dict[str, RegionName] = {}
        self._editing_region: str | None = None
        self._name_input: ui.input | None = None

    def set_regions(self, regions: list[dict[str, object]]) -> None:
        """Update the regions list."""
        self.regions = regions
        self._refresh()

    def load_names(self, names: dict[str, RegionName]) -> None:
        """Load existing region names."""
        self._names = names
        self._refresh()

    def get_names(self) -> dict[str, RegionName]:
        """Get all region names."""
        return self._names

    def _propose_name(self, region_id: str) -> None:
        """Open dialog to propose a name for a region."""
        self._editing_region = region_id
        existing = self._names.get(region_id)
        default_name = existing.name if existing else ""

        with ui.dialog() as dialog, ui.card().classes("w-[500px] p-6"):
            ui.label("Name this region").classes("text-h6 mb-2")
            ui.label(f"Region: {region_id}").classes("text-caption text-grey mb-4")

            self._name_input = (
                ui
                .input("Plain name", value=default_name)
                .props("dense outlined")
                .classes("w-full")
            )

            with ui.row().classes("w-full justify-end gap-2 mt-4"):
                ui.button(
                    "Cancel",
                    on_click=dialog.close,
                ).props("flat")

                def _save() -> None:
                    name = (
                        self._name_input.value.strip()
                        if self._name_input and self._name_input.value
                        else ""
                    )
                    if name:
                        self._save_name(region_id, name)
                    dialog.close()

                ui.button(
                    "Save",
                    on_click=_save,
                    color="primary",
                )

                if existing and not existing.reverted:

                    def _revert() -> None:
                        self._revert_name(region_id)
                        dialog.close()

                    ui.button(
                        "Revert",
                        on_click=_revert,
                        color="negative",
                    ).props("flat")

        dialog.open()

    def _save_name(self, region_id: str, name: str) -> None:
        """Save a proposed name."""
        import time

        existing = self._names.get(region_id)
        version = existing.version + 1 if existing else 1

        new_name = RegionName(
            region_id=region_id,
            name=name,
            proposed_by="user",  # Would be actual user in multi-user
            timestamp=time.time(),
            version=version,
        )
        self._names[region_id] = new_name

        if self.on_propose:
            self.on_propose(region_id, name, version)

        self._refresh()

    def _revert_name(self, region_id: str) -> None:
        """Revert a region name."""
        existing = self._names.get(region_id)
        if existing:
            reverted = RegionName(
                region_id=existing.region_id,
                name=existing.name,
                proposed_by=existing.proposed_by,
                timestamp=existing.timestamp,
                version=existing.version,
                reverted=True,
            )
            self._names[region_id] = reverted
            self._refresh()

    def render(self) -> ui.element:
        """Render the region naming panel."""
        with ui.column().classes("w-full gap-4") as panel:
            self.render_header("Region Names")

            if not self.regions:
                ui.label("No regions to name — run a campaign first.").classes(
                    "text-grey"
                )
                return panel

            ui.label("Click a region to give it a plain name").classes(
                "text-body text-grey"
            )

            with ui.row().classes("w-full gap-4 flex-wrap"):
                for region in self.regions:
                    self._render_region_card(region)

        return panel

    def _render_region_card(self, region: dict[str, object]) -> None:
        """Render a single region card."""
        region_id = str(region.get("region_id", region.get("id", "")))
        if not region_id:
            return

        existing_name = self._names.get(region_id)
        display_name = (
            existing_name.name
            if existing_name and not existing_name.reverted
            else "Unnamed"
        )
        is_named = existing_name is not None and not existing_name.reverted

        with (
            ui.card().classes("flex-1 min-w-[250px]").props("flat bordered"),
            ui.row().classes("w-full items-center gap-2"),
        ):
            ui.icon(ICONS["region"]).classes("text-xl text-primary")
            ui.label(display_name).classes(
                "text-bold flex-1" + (" text-grey" if not is_named else "")
            )
            if is_named and existing_name:
                ui.badge(f"v{existing_name.version}", color="primary").props(
                    "outline"
                ).classes("text-xs")

        ui.separator()

        with ui.row().classes("w-full justify-end gap-2"):
            ui.button(
                "Rename" if is_named else "Name",
                on_click=lambda _=None, rid=region_id: self._propose_name(rid),
            ).props("flat dense color=primary").classes("text-sm")

    def _refresh(self) -> None:
        """Refresh with current data."""


def create_region_naming(
    regions: list[dict[str, object]] | None = None,
) -> RegionNaming:
    """Create the region naming component."""
    return RegionNaming(regions=regions)
