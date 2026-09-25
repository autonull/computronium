"""Extensible View Registry (A3) — declarative panel/view registration.

Replaces the old PanelRegistry with a cleaner, extensible model:
- Views: top-level navigation targets (Monitor, Atlas, Repair, Compose)
- Panels: composable UI units that can live in views, modals, drawers, or tabs
- Extensions: optional features (gamify, workshop, command palette) toggled by flags
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Any, Callable

from computronium.ui.data_adapters import DataAdapter as Adapter
from computronium.ui.mode_toggle import BasePanel, Register as UIMode

if TYPE_CHECKING:
    from pathlib import Path

    from computronium.visualization.live_atlas import DashboardSnapshot


class ViewMode(Enum):
    """Visibility modes for views/panels."""

    ALWAYS = "always"  # Visible in both explorer and lab
    EXPLORER = "explorer"  # Only in explorer mode
    LAB = "lab"  # Only in lab mode
    GAMIFY = "gamify"  # Only when gamify is on
    UI_ACTIONS = "ui_actions"  # Only when --ui-actions is on


class PanelPlacement(Enum):
    """Where a panel can be rendered."""

    VIEW = "view"  # Full view container (top-level nav)
    TAB = "tab"  # Tab within a view
    MODAL = "modal"  # Modal dialog
    DRAWER = "drawer"  # Side drawer
    OVERLAY = "overlay"  # Floating overlay (badges, toasts)


@dataclass(frozen=True, slots=True)
class PanelSpec:
    """Specification for a composable panel."""

    key: str
    label_key: str  # Glossary key for i18n
    icon: str
    factory: Callable[[], BasePanel]
    adapter_key: str | None = None
    placement: PanelPlacement = PanelPlacement.VIEW
    modes: tuple[ViewMode, ...] = (ViewMode.ALWAYS,)
    parent_view: str | None = None  # For tabs: which view they belong to
    order: int = 0
    hotkey: str | None = None  # e.g., "1", "2", "g", "w"

    def visible_in(self, mode: UIMode, gamify: bool, ui_actions: bool) -> bool:
        """Check if panel should be visible given current mode/flags."""
        for m in self.modes:
            if m == ViewMode.ALWAYS:
                return True
            if m == ViewMode.EXPLORER and mode == "explorer":
                return True
            if m == ViewMode.LAB and mode == "lab":
                return True
            if m == ViewMode.GAMIFY and gamify:
                return True
            if m == ViewMode.UI_ACTIONS and ui_actions:
                return True
        return False


@dataclass(frozen=True, slots=True)
class ViewSpec:
    """Specification for a top-level view."""

    key: str
    label_key: str
    icon: str
    factory: Callable[[], BasePanel]
    adapter_key: str | None = None
    modes: tuple[ViewMode, ...] = (ViewMode.ALWAYS,)
    order: int = 0
    hotkey: str | None = None
    tabs: list[PanelSpec] = field(default_factory=list)  # Child tabs

    def visible_in(self, mode: UIMode, gamify: bool, ui_actions: bool) -> bool:
        for m in self.modes:
            if m == ViewMode.ALWAYS:
                return True
            if m == ViewMode.EXPLORER and mode == "explorer":
                return True
            if m == ViewMode.LAB and mode == "lab":
                return True
            if m == ViewMode.GAMIFY and gamify:
                return True
            if m == ViewMode.UI_ACTIONS and ui_actions:
                return True
        return False


class ViewRegistry:
    """Central registry for views, panels, and extensions.

    Single source of truth for what UI exists and when it's visible.
    """

    def __init__(self) -> None:
        self._views: dict[str, ViewSpec] = {}
        self._panels: dict[str, PanelSpec] = {}
        self._adapters: dict[str, Adapter] = {}
        self._extensions: dict[str, Callable] = {}

    # ------------------------------------------------------------------ Views
    def register_view(self, spec: ViewSpec) -> None:
        """Register a top-level view."""
        self._views[spec.key] = spec
        # Auto-register tabs
        for tab in spec.tabs:
            self._panels[tab.key] = tab

    def get_view(self, key: str) -> ViewSpec | None:
        return self._views.get(key)

    def get_visible_views(
        self, mode: UIMode, gamify: bool, ui_actions: bool
    ) -> list[ViewSpec]:
        """Get all views visible in current mode, sorted by order."""
        return sorted(
            [
                v
                for v in self._views.values()
                if v.visible_in(mode, gamify, ui_actions)
            ],
            key=lambda v: v.order,
        )

    # ------------------------------------------------------------------ Panels
    def register_panel(self, spec: PanelSpec) -> None:
        """Register a composable panel (tab, modal, drawer, overlay)."""
        self._panels[spec.key] = spec

    def get_panel(self, key: str) -> PanelSpec | None:
        return self._panels.get(key)

    def get_panels_for_view(
        self, view_key: str, mode: UIMode, gamify: bool, ui_actions: bool
    ) -> list[PanelSpec]:
        """Get all panels (tabs) for a view, filtered by visibility."""
        return sorted(
            [
                p
                for p in self._panels.values()
                if p.parent_view == view_key
                and p.visible_in(mode, gamify, ui_actions)
            ],
            key=lambda p: p.order,
        )

    def get_all_panels(
        self, mode: UIMode, gamify: bool, ui_actions: bool
    ) -> list[PanelSpec]:
        """Get all panels visible in current mode."""
        return sorted(
            [
                p
                for p in self._panels.values()
                if p.visible_in(mode, gamify, ui_actions)
            ],
            key=lambda p: (p.placement.value, p.order),
        )

    # ------------------------------------------------------------------ Adapters
    def register_adapter(self, key: str, adapter: Adapter) -> None:
        self._adapters[key] = adapter

    def get_adapter(self, key: str) -> Adapter | None:
        return self._adapters.get(key)

    # ------------------------------------------------------------------ Extensions
    def register_extension(self, key: str, factory: Callable) -> None:
        """Register an optional extension (command palette, gamify overlay, etc.)."""
        self._extensions[key] = factory

    def get_extension(self, key: str) -> Callable | None:
        return self._extensions.get(key)

    # ------------------------------------------------------------------ Helpers
    def all_searchable_items(
        self, mode: UIMode, gamify: bool, ui_actions: bool
    ) -> list[dict[str, Any]]:
        """Return all views/panels as searchable items for command palette."""
        items = []
        for v in self.get_visible_views(mode, gamify, ui_actions):
            items.append(
                {
                    "type": "view",
                    "key": v.key,
                    "label": v.label_key,
                    "icon": v.icon,
                    "hotkey": v.hotkey,
                }
            )
        for p in self.get_all_panels(mode, gamify, ui_actions):
            if p.placement != PanelPlacement.VIEW:
                items.append(
                    {
                        "type": "panel",
                        "key": p.key,
                        "label": p.label_key,
                        "icon": p.icon,
                        "placement": p.placement.value,
                        "parent_view": p.parent_view,
                        "hotkey": p.hotkey,
                    }
                )
        return items


# Global registry instance
registry = ViewRegistry()