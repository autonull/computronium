"""Command Palette — Cmd+K quick navigation and actions."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from nicegui import ui

from computronium.ui.mode_toggle import BasePanel, tr
from computronium.ui.view_registry import PanelPlacement, registry

if TYPE_CHECKING:
    from computronium.ui.dashboard import DashboardApp


@dataclass(frozen=True, slots=True)
class PaletteItem:
    """An item in the command palette."""

    key: str
    label: str
    icon: str
    description: str = ""
    action: Callable[[], None] | None = None
    category: str = "navigation"
    hotkey: str | None = None


class CommandPalette(BasePanel):
    """Cmd+K command palette for quick navigation and actions."""

    def __init__(self, app: DashboardApp) -> None:
        super().__init__(
            panel_key="command_palette",
            plain_explanation="Quick access to all views, panels, and actions",
            why_explanation="Type to search and jump anywhere without clicking through menus",
            expert_explanation="Fuzzy search over registered views, panels, and extensions. Extensible via ViewRegistry.",
            docs_url="https://github.com/computronium/dashboard#command-palette",
        )
        self._app = app
        self._dialog: ui.dialog | None = None
        self._input: ui.input | None = None
        self._list: ui.column | None = None
        self._items: list[PaletteItem] = []
        self._filtered: list[PaletteItem] = []
        self._selected_idx = 0
        self._visible = False

    def build(self) -> None:
        """Build the palette dialog (call once at app startup)."""
        self._dialog = ui.dialog().props("persistent")
        with self._dialog, ui.card().classes("w-[600px] max-w-[90vw] p-0"):
            # Search input
            self._input = (
                ui
                .input(
                    placeholder="Type a command or search...",
                    on_change=self._filter,
                )
                .props("dense outlined autofocus")
                .classes("w-full mb-2")
            )
            self._input.on("keydown.up", self._nav_up)
            self._input.on("keydown.down", self._nav_down)
            self._input.on("keydown.enter", self._activate)
            self._input.on("keydown.escape", self.hide)

            # Results list
            self._list = ui.column().classes("w-full max-h-[400px] overflow-auto")

        # Global keyboard shortcut: Cmd/Ctrl+K
        ui.keyboard(on_key=self._on_global_key)

    def _on_global_key(self, e: Any) -> None:
        """Handle global Cmd/Ctrl+K."""
        if (e.key == "k" or e.key == "K") and (e.meta or e.ctrl):
            e.preventDefault()
            self.toggle()

    def toggle(self) -> None:
        """Show/hide the palette."""
        if self._visible:
            self.hide()
        else:
            self.show()

    def show(self) -> None:
        """Show the palette with fresh items."""
        self._rebuild_items()
        self._filter()
        self._selected_idx = 0
        self._highlight_selection()
        if self._dialog:
            self._dialog.open()
        if self._input:
            self._input.focus()
        self._visible = True

    def hide(self) -> None:
        """Hide the palette."""
        if self._dialog:
            self._dialog.close()
        self._visible = False

    @property
    def is_open(self) -> bool:
        """Whether the palette dialog is open (for global-hotkey guards)."""
        return self._visible

    def _rebuild_items(self) -> None:
        """Rebuild items from registry and app actions."""
        self._items = []

        # Views
        mode = self._app.ui_mode
        gamify = getattr(self._app, "gamify", False)
        ui_actions = getattr(self._app, "ui_actions", False)
        for item in registry.all_searchable_items(mode, gamify, ui_actions):
            if item["type"] == "view":
                self._items.append(
                    PaletteItem(
                        key=f"view:{item['key']}",
                        label=tr(item["label"], mode),
                        icon=item["icon"],
                        description=f"Switch to {tr(item['label'], mode)} view",
                        action=lambda k=item["key"]: self._app.switch_view(k),
                        category="view",
                        hotkey=item.get("hotkey"),
                    )
                )

        # Panels (modals, drawers, overlays)
        for item in registry.all_searchable_items(mode, gamify, ui_actions):
            if item["type"] == "panel":
                self._items.append(
                    PaletteItem(
                        key=f"panel:{item['key']}",
                        label=tr(item["label"], mode),
                        icon=item["icon"],
                        description=f"Open {tr(item['label'], mode)} ({item['placement']})",
                        action=lambda k=item["key"]: self._open_panel(k),
                        category="panel",
                        hotkey=item.get("hotkey"),
                    )
                )

        # App actions
        self._items.extend([
            PaletteItem(
                key="action:refresh",
                label=tr("refresh_now"),
                icon="refresh",
                description="Force refresh all data",
                action=self._app.force_refresh,
                category="action",
                hotkey="r",
            ),
            PaletteItem(
                key="action:toggle_mode",
                label=tr("toggle_mode"),
                icon="swap_horiz",
                description="Switch Explorer ↔ Lab mode",
                action=self._app.toggle_mode,
                category="action",
                hotkey="m",
            ),
            PaletteItem(
                key="action:toggle_quiet",
                label=tr("toggle_quiet"),
                icon="volume_off",
                description="Toggle quiet mode (compact feed)",
                action=self._app.toggle_quiet,
                category="action",
                hotkey="q",
            ),
        ])

        # Extension actions
        if gamify:
            self._items.append(
                PaletteItem(
                    key="action:badges",
                    label=tr("badges"),
                    icon="emoji_events",
                    description="View badges and quests",
                    action=lambda: self._open_panel("progress"),
                    category="gamify",
                    hotkey="b",
                )
            )
        if ui_actions:
            self._items.append(
                PaletteItem(
                    key="action:workshop",
                    label=tr("workshop"),
                    icon="build",
                    description="Open recipe workshop",
                    action=lambda: self._open_panel("workshop"),
                    category="workshop",
                    hotkey="w",
                )
            )

    def _filter(self, *args: Any) -> None:
        """Filter items by search query."""
        query = (self._input.value or "").lower().strip() if self._input else ""
        if not query:
            self._filtered = self._items[:]
        else:
            self._filtered = [
                item
                for item in self._items
                if query in item.label.lower()
                or query in item.description.lower()
                or query in item.key.lower()
                or (item.hotkey and query == item.hotkey.lower())
            ]
        self._selected_idx = 0
        self._render_list()

    def _render_list(self) -> None:
        """Render filtered items."""
        if not self._list:
            return
        self._list.clear()
        with self._list:
            if not self._filtered:
                ui.label("No matches").classes("text-grey p-4 text-center")
                return

            current_category = None
            for idx, item in enumerate(self._filtered):
                if item.category != current_category:
                    current_category = item.category
                    ui.label(current_category.title()).classes(
                        "text-xs text-grey px-3 py-1 font-bold"
                    )

                with (
                    ui
                    .row()
                    .classes(
                        "w-full items-center gap-3 px-3 py-2 cursor-pointer hover:bg-grey-2"
                        + (
                            " bg-primary text-white"
                            if idx == self._selected_idx
                            else ""
                        )
                    )
                    .on("click", lambda i=item: self._activate_item(i))
                ) as row:
                    ui.icon(item.icon).classes("text-lg")
                    ui.label(item.label).classes("flex-1")
                    if item.hotkey:
                        ui.label(item.hotkey.upper()).classes(
                            "text-xs text-grey-6 px-2 py-0.5 rounded bg-grey-3"
                        )
                    if item.description:
                        ui.label(item.description).classes("text-xs text-grey")

    def _nav_up(self, *args: Any) -> None:
        if self._filtered:
            self._selected_idx = (self._selected_idx - 1) % len(self._filtered)
            self._highlight_selection()

    def _nav_down(self, *args: Any) -> None:
        if self._filtered:
            self._selected_idx = (self._selected_idx + 1) % len(self._filtered)
            self._highlight_selection()

    def _activate(self, *args: Any) -> None:
        if self._filtered and 0 <= self._selected_idx < len(self._filtered):
            self._activate_item(self._filtered[self._selected_idx])

    def _activate_item(self, item: PaletteItem) -> None:
        if item.action:
            item.action()
        self.hide()

    def _highlight_selection(self) -> None:
        self._render_list()

    def _open_panel(self, panel_key: str) -> None:
        """Open a panel (modal/drawer/overlay)."""
        spec = registry.get_panel(panel_key)
        if spec and spec.placement == PanelPlacement.MODAL:
            panel = spec.factory()
            panel.render()  # This should create its own dialog
        elif spec and spec.placement == PanelPlacement.DRAWER:
            # Right drawer panels handled by view
            pass

    # Required by BasePanel
    def render(self) -> ui.element:
        return ui.element("div")  # Never rendered directly

    def update_data(self, data: object | None = None, **kwargs: object) -> None:
        pass


def create_command_palette(app: DashboardApp) -> CommandPalette:
    """Factory for CommandPalette."""
    return CommandPalette(app)
