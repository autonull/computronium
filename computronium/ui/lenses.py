"""Lens system — shared projection framework for panels.

A Lens is a named projection (view) within a panel. Only panels where
projections are genuinely shared (Map, Repair, Record) have lenses.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Callable

    from nicegui import ui


@dataclass(frozen=True, slots=True)
class LensSpec:
    """Specification for a lens within a panel."""

    key: str
    label: str
    icon: str
    render: Callable[[Any], ui.element]  # panel instance -> ui element
    register_default: str = "both"  # "explorer" | "lab" | "both"


class LensRegistry:
    """Registry of lenses per panel."""

    def __init__(self) -> None:
        self._lenses: dict[str, dict[str, LensSpec]] = {}

    def register(
        self,
        panel_key: str,
        lens_key: str,
        label: str,
        icon: str,
        render: Callable[[Any], ui.element],
        *,
        register_default: str = "both",
    ) -> LensSpec:
        """Register a lens for a panel."""
        if panel_key not in self._lenses:
            self._lenses[panel_key] = {}
        spec = LensSpec(
            key=lens_key,
            label=label,
            icon=icon,
            render=render,
            register_default=register_default,
        )
        self._lenses[panel_key][lens_key] = spec
        return spec

    def get(self, panel_key: str, lens_key: str) -> LensSpec | None:
        """Get a lens spec."""
        return self._lenses.get(panel_key, {}).get(lens_key)

    def all_for_panel(self, panel_key: str) -> dict[str, LensSpec]:
        """Get all lenses for a panel."""
        return self._lenses.get(panel_key, {})

    def default_for_panel(self, panel_key: str, register: str) -> str | None:
        """Get the default lens key for a panel/register combination."""
        lenses = self._lenses.get(panel_key, {})
        valid_defaults = {register, "both"}
        for key, spec in lenses.items():
            if spec.register_default in valid_defaults:
                return key
        return next(iter(lenses)) if lenses else None


# Global lens registry
lens_registry = LensRegistry()


# Panel lens keys
class PanelLenses:
    """Known panel lens keys."""

    MAP = "map"
    REPAIR = "repair"
    CONSOLE = "console"
    COMPOSER = "composer"
    RECORD = "record"


# Lens keys per panel
class MapLens:
    MAP = "map"
    TRADEOFFS = "tradeoffs"
    GALLERY = "gallery"


class RepairLens:
    DEFECTS = "defects"
    MATURATION = "maturation"


class RecordLens:
    HISTORY = "history"
    LEDGER = "ledger"
    LESSONS = "lessons"


# Palette deep-link format: "panel:lens"
def palette_deep_link(panel: str, lens: str) -> str:
    """Generate a palette deep-link string."""
    return f"{panel}:{lens}"


def parse_deep_link(link: str) -> tuple[str, str] | None:
    """Parse a palette deep-link string."""
    parts = link.split(":", 1)
    if len(parts) == 2:
        return parts[0], parts[1]
    return None


__all__ = [
    "LensRegistry",
    "LensSpec",
    "MapLens",
    "PanelLenses",
    "RecordLens",
    "RepairLens",
    "lens_registry",
    "palette_deep_link",
    "parse_deep_link",
]
