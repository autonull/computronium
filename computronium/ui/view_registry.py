"""Extensible View Registry — declarative panel/view registration.

Single register: views and panels carry plain-language labels directly.
No mode gating, no flag gating — progress and workshop are always available
via the command palette. Cross-panel interaction state (selection, filters,
density, scrub cursor) lives in ``ui/state.py``; panels never do I/O.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from computronium.ui.data_adapters import DataAdapter as Adapter


class PanelPlacement(Enum):
    """Where a panel can be rendered."""

    PAGE = "page"  # Full view container (top-level nav)
    TAB = "tab"  # Tab within a view
    MODAL = "modal"  # Modal dialog (progress, workshop)
    DRAWER = "drawer"  # Side drawer (cell forensics, explanations)


@dataclass(frozen=True, slots=True)
class PanelSpec:
    """Specification for a composable panel."""

    key: str
    label: str
    icon: str
    factory: Callable[[], Any]
    adapter_key: str | None = None
    placement: PanelPlacement = PanelPlacement.PAGE
    parent_view: str | None = None  # For tabs: which view they belong to
    order: int = 0
    hotkey: str | None = None  # e.g., "1", "2", "b", "w"


@dataclass(frozen=True, slots=True)
class ViewSpec:
    """Specification for a top-level view."""

    key: str
    label: str
    icon: str
    factory: Callable[[], Any]
    adapter_key: str | None = None
    order: int = 0
    hotkey: str | None = None
    tabs: list[PanelSpec] = field(default_factory=list)  # Child tabs


class ViewRegistry:
    """Central registry for views, panels, and extensions.

    Single source of truth for what UI exists.
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

    def get_visible_views(self) -> list[ViewSpec]:
        """All views sorted by order."""
        return sorted(self._views.values(), key=lambda v: v.order)

    # ------------------------------------------------------------------ Panels
    def register_panel(self, spec: PanelSpec) -> None:
        """Register a composable panel (tab, modal, drawer)."""
        self._panels[spec.key] = spec

    def get_panel(self, key: str) -> PanelSpec | None:
        return self._panels.get(key)

    def get_panels_for_view(self, view_key: str) -> list[PanelSpec]:
        """All tab panels for a view, sorted by order."""
        return sorted(
            [p for p in self._panels.values() if p.parent_view == view_key],
            key=lambda p: p.order,
        )

    def get_all_panels(self) -> list[PanelSpec]:
        """All registered panels."""
        return sorted(self._panels.values(), key=lambda p: (p.placement.value, p.order))

    # ------------------------------------------------------------------ Adapters
    def register_adapter(self, key: str, adapter: Adapter) -> None:
        self._adapters[key] = adapter

    def get_adapter(self, key: str) -> Adapter | None:
        return self._adapters.get(key)

    # ------------------------------------------------------------------ Extensions
    def register_extension(self, key: str, factory: Callable) -> None:
        """Register an optional extension (command palette, overlay, etc.)."""
        self._extensions[key] = factory

    def get_extension(self, key: str) -> Callable | None:
        return self._extensions.get(key)

    # ------------------------------------------------------------------ Helpers
    def all_searchable_items(self) -> list[dict[str, Any]]:
        """All views/panels as searchable items for the command palette."""
        items = []
        for v in self.get_visible_views():
            items.append({
                "type": "view",
                "key": v.key,
                "label": v.label,
                "icon": v.icon,
                "hotkey": v.hotkey,
            })
        for p in self.get_all_panels():
            if p.placement != PanelPlacement.PAGE:
                items.append({
                    "type": "panel",
                    "key": p.key,
                    "label": p.label,
                    "icon": p.icon,
                    "placement": p.placement.value,
                    "parent_view": p.parent_view,
                    "hotkey": p.hotkey,
                })
        return items


# Global registry instance
registry = ViewRegistry()
