"""Computronium UI package — mission-control dashboard (GAME.todo7).

Public API:
- BasePanel — base class for all dashboard panels (single register,
  plain labels, "What am I looking at?" drawer, lifecycle hooks)
- design_tokens — colorblind-safe palettes, type scale, icons, focus styles
"""

from __future__ import annotations

# Design tokens
from computronium.ui.design_tokens import (
    BORDER_RADIUS,
    BREAKPOINTS,
    CATEGORICAL_VIRIDIS,
    DENSITY_TOKENS,
    DIVERGING,
    EVENT_COLORS,
    FOCUS_RING,
    FONT_WEIGHT,
    GRAYSCALE,
    HIGH_CONTRAST_CSS,
    ICONS,
    LINE_HEIGHT,
    OUTCOME_COLORS,
    PRIMARY,
    REDUCED_MOTION_CSS,
    SECONDARY,
    SEMANTIC,
    SEQUENTIAL_CIVIDIS,
    SHADOWS,
    SPACING,
    TRANSITIONS,
    TYPE_SCALE,
    Z_INDEX,
    DensityTokens,
    css_custom_properties,
    get_density_tokens,
)

# Panel base
from computronium.ui.panels import BasePanel

__all__ = [
    "BORDER_RADIUS",
    "BREAKPOINTS",
    "CATEGORICAL_VIRIDIS",
    "DENSITY_TOKENS",
    "DIVERGING",
    "EVENT_COLORS",
    "FOCUS_RING",
    "FONT_WEIGHT",
    "GRAYSCALE",
    "HIGH_CONTRAST_CSS",
    "ICONS",
    "LINE_HEIGHT",
    "OUTCOME_COLORS",
    "PRIMARY",
    "REDUCED_MOTION_CSS",
    "SECONDARY",
    "SEMANTIC",
    "SEQUENTIAL_CIVIDIS",
    "SHADOWS",
    "SPACING",
    "TRANSITIONS",
    "TYPE_SCALE",
    "Z_INDEX",
    "BasePanel",
    "DensityTokens",
    "css_custom_properties",
    "get_density_tokens",
]
