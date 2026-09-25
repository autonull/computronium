"""Computronium UI package — inclusive gamified dashboard (TODO-UX1).

Public API:
- GlossaryService, tr, tr_both — register-aware string lookup
- get_mode, set_mode, initialize_mode — Explorer/Lab mode toggle
- mode_toggle_button, mode_toggle_select — UI components for mode switching
- BasePanel — base class for all dashboard panels
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

# Glossary
from computronium.ui.glossary_service import (
    GlossaryService,
    get_glossary_service,
    tr,
    tr_both,
)

# Mode toggle
from computronium.ui.mode_toggle import (
    BasePanel,
    GlossaryAware,
    Register,
    get_mode,
    initialize_mode,
    mode_toggle_button,
    mode_toggle_select,
    set_mode,
)

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
    "GlossaryAware",
    "GlossaryService",
    "Register",
    "css_custom_properties",
    "get_density_tokens",
    "get_glossary_service",
    "get_mode",
    "initialize_mode",
    "mode_toggle_button",
    "mode_toggle_select",
    "set_mode",
    "tr",
    "tr_both",
]
