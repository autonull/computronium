"""Theming System — design tokens, CSS variables, and theme management.

Integrates with existing design_tokens.py and provides:
- Semantic color tokens (primary, secondary, surface, etc.)
- Spacing, typography, border radius scales
- Dark/light mode support
- CSS variable injection for NiceGUI
- Theme switching at runtime
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, ClassVar

from computronium.ui.design_tokens import (
    PRIMARY,
    SECONDARY,
    SPACING,
    BORDER_RADIUS,
    SHADOWS,
    Z_INDEX,
    TRANSITIONS,
    css_custom_properties,
    SEMANTIC,
)


@dataclass(frozen=True, slots=True)
class ColorTokens:
    """Semantic color palette."""

    # Primary brand colors
    primary: str = PRIMARY
    primary_hover: str = "#1e40af"  # darker
    primary_light: str = "#3b82f6"  # lighter
    primary_contrast: str = "#ffffff"

    # Secondary brand colors
    secondary: str = SECONDARY
    secondary_hover: str = "#0f766e"
    secondary_light: str = "#14b8a6"
    secondary_contrast: str = "#ffffff"

    # Semantic status colors (from design_tokens.SEMANTIC)
    success: str = SEMANTIC["success"]
    success_hover: str = "#16a34a"
    success_light: str = "#22c55e"
    success_contrast: str = "#ffffff"

    warning: str = SEMANTIC["warning"]
    warning_hover: str = "#ca8a04"
    warning_light: str = "#eab308"
    warning_contrast: str = "#1f2937"

    error: str = SEMANTIC["danger"]
    error_hover: str = "#dc2626"
    error_light: str = "#ef4444"
    error_contrast: str = "#ffffff"

    info: str = SEMANTIC["info"]
    info_hover: str = "#0284c7"
    info_light: str = "#06b6d4"
    info_contrast: str = "#ffffff"

    # Neutral/surface colors (light mode)
    surface: str = "#ffffff"
    surface_variant: str = "#f8fafc"
    surface_elevated: str = "#ffffff"
    surface_hover: str = "#f1f5f9"

    background: str = "#f8fafc"
    background_secondary: str = "#f1f5f9"

    border: str = "#e2e8f0"
    border_strong: str = "#cbd5e1"
    border_focus: str = PRIMARY

    text_primary: str = "#0f172a"
    text_secondary: str = "#475569"
    text_tertiary: str = "#94a3b8"
    text_inverse: str = "#ffffff"
    text_disabled: str = "#cbd5e1"

    # Dark mode overrides
    dark_surface: str = "#1e293b"
    dark_surface_variant: str = "#0f172a"
    dark_surface_elevated: str = "#1e293b"
    dark_surface_hover: str = "#334155"

    dark_background: str = "#0f172a"
    dark_background_secondary: str = "#1e293b"

    dark_border: str = "#334155"
    dark_border_strong: str = "#475569"
    dark_border_focus: str = "#3b82f6"

    dark_text_primary: str = "#f1f5f9"
    dark_text_secondary: str = "#cbd5e1"
    dark_text_tertiary: str = "#64748b"
    dark_text_inverse: str = "#0f172a"
    dark_text_disabled: str = "#475569"


@dataclass(frozen=True, slots=True)
class SpacingTokens:
    """Spacing scale (based on 4px base unit)."""

    none: str = "0"
    xs: str = "0.25rem"   # 4px
    sm: str = "0.5rem"    # 8px
    md: str = "1rem"      # 16px
    lg: str = "1.5rem"    # 24px
    xl: str = "2rem"      # 32px
    xxl: str = "3rem"     # 48px
    xxxl: str = "4rem"    # 64px

    # Component-specific
    card_padding: str = "1.5rem"
    card_gap: str = "1rem"
    section_gap: str = "2rem"
    page_padding: str = "1.5rem"
    modal_padding: str = "1.5rem"


@dataclass(frozen=True, slots=True)
class TypographyTokens:
    """Typography scale."""

    font_family: str = "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
    font_family_mono: str = "'JetBrains Mono', 'Fira Code', Consolas, monospace"

    # Font sizes (clamp for fluid scaling)
    xs: str = "clamp(0.7rem, 0.65rem + 0.25vw, 0.75rem)"
    sm: str = "clamp(0.8rem, 0.75rem + 0.25vw, 0.875rem)"
    base: str = "clamp(0.9rem, 0.85rem + 0.25vw, 1rem)"
    lg: str = "clamp(1.05rem, 1rem + 0.25vw, 1.125rem)"
    xl: str = "clamp(1.2rem, 1.125rem + 0.375vw, 1.375rem)"
    xxl: str = "clamp(1.5rem, 1.375rem + 0.625vw, 1.875rem)"
    xxxl: str = "clamp(2rem, 1.75rem + 1.25vw, 2.5rem)"

    # Font weights
    normal: int = 400
    medium: int = 500
    semibold: int = 600
    bold: int = 700

    # Line heights
    tight: float = 1.2
    normal_lh: float = 1.5
    relaxed: float = 1.75

    # Letter spacing
    tight_ls: str = "-0.02em"
    normal_ls: str = "0"
    wide_ls: str = "0.02em"


@dataclass(frozen=True, slots=True)
class BorderRadiusTokens:
    """Border radius scale."""

    none: str = "0"
    sm: str = "0.25rem"
    md: str = "0.375rem"
    lg: str = "0.5rem"
    xl: str = "0.75rem"
    xxl: str = "1rem"
    full: str = "9999px"

    card: str = "0.75rem"
    modal: str = "1rem"
    button: str = "0.5rem"
    input: str = "0.375rem"
    badge: str = "0.25rem"


@dataclass(frozen=True, slots=True)
class ShadowTokens:
    """Box shadow scale."""

    none: str = "none"
    xs: str = "0 1px 2px 0 rgb(0 0 0 / 0.05)"
    sm: str = "0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)"
    md: str = "0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)"
    lg: str = "0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)"
    xl: str = "0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)"
    xxl: str = "0 25px 50px -12px rgb(0 0 0 / 0.25)"

    # Component-specific
    card: str = "0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)"
    modal: str = "0 25px 50px -12px rgb(0 0 0 / 0.25)"
    dropdown: str = "0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)"
    tooltip: str = "0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)"


@dataclass(frozen=True, slots=True)
class ZIndexTokens:
    """Z-index scale."""

    base: int = 0
    dropdown: int = 1000
    sticky: int = 1100
    fixed: int = 1200
    modal_backdrop: int = 1300
    modal: int = 1400
    popover: int = 1500
    tooltip: int = 1600
    toast: int = 1700
    max: int = 2147483647


@dataclass(frozen=True, slots=True)
class TransitionTokens:
    """Transition/animation tokens."""

    fast: str = "100ms ease"
    normal: str = "150ms ease"
    slow: str = "200ms ease"
    slower: str = "300ms ease"

    # Easing curves
    ease_in: str = "cubic-bezier(0.4, 0, 1, 1)"
    ease_out: str = "cubic-bezier(0, 0, 0.2, 1)"
    ease_in_out: str = "cubic-bezier(0.4, 0, 0.2, 1)"
    spring: str = "cubic-bezier(0.68, -0.55, 0.265, 1.55)"

    # Component-specific
    color: str = "color 150ms ease, background-color 150ms ease, border-color 150ms ease"
    transform: str = "transform 150ms ease"
    opacity: str = "opacity 150ms ease"
    all: str = "all 150ms ease"


@dataclass(frozen=True, slots=True)
class BreakpointTokens:
    """Responsive breakpoints."""

    sm: str = "640px"
    md: str = "768px"
    lg: str = "1024px"
    xl: str = "1280px"
    xxl: str = "1536px"


@dataclass(frozen=True, slots=True)
class Theme:
    """Complete theme configuration."""

    name: str
    colors: ColorTokens = field(default_factory=ColorTokens)
    spacing: SpacingTokens = field(default_factory=SpacingTokens)
    typography: TypographyTokens = field(default_factory=TypographyTokens)
    border_radius: BorderRadiusTokens = field(default_factory=BorderRadiusTokens)
    shadows: ShadowTokens = field(default_factory=ShadowTokens)
    z_index: ZIndexTokens = field(default_factory=ZIndexTokens)
    transitions: TransitionTokens = field(default_factory=TransitionTokens)
    breakpoints: BreakpointTokens = field(default_factory=BreakpointTokens)

    def to_css_variables(self, prefix: str = "ct") -> str:
        """Generate CSS custom properties for this theme."""
        lines = [f":root {{"]
        for category, tokens in [
            ("color", self.colors),
            ("space", self.spacing),
            ("font", self.typography),
            ("radius", self.border_radius),
            ("shadow", self.shadows),
            ("z", self.z_index),
            ("transition", self.transitions),
            ("bp", self.breakpoints),
        ]:
            for key, value in tokens.__dict__.items():
                if not key.startswith("_"):
                    css_key = f"--{prefix}-{category}-{key.replace('_', '-')}"
                    lines.append(f"  {css_key}: {value};")
        lines.append("}")
        return "\n".join(lines)


# ──────────────────────────────────────────────────────────────────────────────
# Built-in Themes
# ──────────────────────────────────────────────────────────────────────────────

LIGHT_THEME = Theme(
    name="light",
    colors=ColorTokens(),
)

DARK_THEME = Theme(
    name="dark",
    colors=ColorTokens(
        surface="#1e293b",
        surface_variant="#0f172a",
        surface_elevated="#1e293b",
        surface_hover="#334155",
        background="#0f172a",
        background_secondary="#1e293b",
        border="#334155",
        border_strong="#475569",
        border_focus="#3b82f6",
        text_primary="#f1f5f9",
        text_secondary="#cbd5e1",
        text_tertiary="#64748b",
        text_inverse="#0f172a",
        text_disabled="#475569",
    ),
)


# ──────────────────────────────────────────────────────────────────────────────
# Theme Manager
# ──────────────────────────────────────────────────────────────────────────────

class ThemeManager:
    """Manages active theme and CSS injection."""

    def __init__(self) -> None:
        self._theme = LIGHT_THEME
        self._injected = False

    @property
    def theme(self) -> Theme:
        return self._theme

    @property
    def is_dark(self) -> bool:
        return self._theme.name == "dark"

    def set_theme(self, theme: Theme | str) -> None:
        """Switch theme."""
        if isinstance(theme, str):
            theme = DARK_THEME if theme == "dark" else LIGHT_THEME
        self._theme = theme
        self._inject_css()

    def toggle_dark(self) -> None:
        """Toggle between light and dark."""
        self.set_theme(DARK_THEME if self.is_dark else LIGHT_THEME)

    def _inject_css(self) -> None:
        """Inject theme CSS variables into page."""
        from nicegui import ui
        css = self._theme.to_css_variables()
        # Also include original design tokens
        css += "\n" + css_custom_properties()
        ui.add_head_html(f"<style id='computronium-theme'>{css}</style>")

    def get_css_variables(self) -> str:
        """Get CSS variables for current theme."""
        return self._theme.to_css_variables()


theme_manager = ThemeManager()


# ──────────────────────────────────────────────────────────────────────────────
# Component Styling Helpers
# ──────────────────────────────────────────────────────────────────────────────

class StyleBuilder:
    """Fluent API for building component styles."""

    def __init__(self) -> None:
        self._props: dict[str, str] = {}

    def color(self, value: str) -> "StyleBuilder":
        self._props["color"] = value
        return self

    def bg(self, value: str) -> "StyleBuilder":
        self._props["background-color"] = value
        return self

    def padding(self, value: str) -> "StyleBuilder":
        self._props["padding"] = value
        return self

    def margin(self, value: str) -> "StyleBuilder":
        self._props["margin"] = value
        return self

    def gap(self, value: str) -> "StyleBuilder":
        self._props["gap"] = value
        return self

    def radius(self, value: str) -> "StyleBuilder":
        self._props["border-radius"] = value
        return self

    def shadow(self, value: str) -> "StyleBuilder":
        self._props["box-shadow"] = value
        return self

    def font_size(self, value: str) -> "StyleBuilder":
        self._props["font-size"] = value
        return self

    def font_weight(self, value: int | str) -> "StyleBuilder":
        self._props["font-weight"] = str(value)
        return self

    def transition(self, value: str) -> "StyleBuilder":
        self._props["transition"] = value
        return self

    def build(self) -> str:
        return "; ".join(f"{k}: {v}" for k, v in self._props.items())

    def apply(self, element: Any) -> Any:
        element.style(self.build())
        return element


def style() -> StyleBuilder:
    """Create a new style builder."""
    return StyleBuilder()


# Semantic style helpers
def card_style(elevated: bool = False) -> StyleBuilder:
    """Card container style."""
    t = theme_manager.theme
    s = style().padding(t.spacing.card_padding).gap(t.spacing.card_gap)
    s = s.radius(t.border_radius.card).bg(t.colors.surface if not elevated else t.colors.surface_elevated)
    s = s.shadow(t.shadows.card if not elevated else t.shadows.lg)
    return s


def button_style(variant: str = "primary", size: str = "md") -> StyleBuilder:
    """Button style."""
    t = theme_manager.theme
    colors = {
        "primary": (t.colors.primary, t.colors.primary_contrast),
        "secondary": (t.colors.secondary, t.colors.secondary_contrast),
        "success": (t.colors.success, t.colors.success_contrast),
        "warning": (t.colors.warning, t.colors.warning_contrast),
        "error": (t.colors.error, t.colors.error_contrast),
        "info": (t.colors.info, t.colors.info_contrast),
        "ghost": ("transparent", t.colors.text_primary),
        "outline": ("transparent", t.colors.text_primary),
    }
    bg, fg = colors.get(variant, colors["primary"])

    padding_map = {
        "xs": (t.spacing.xs, t.spacing.sm),
        "sm": (t.spacing.sm, t.spacing.md),
        "md": (t.spacing.md, t.spacing.lg),
        "lg": (t.spacing.lg, t.spacing.xl),
    }
    py, px = padding_map.get(size, padding_map["md"])

    s = style().bg(bg).color(fg).padding(f"{py} {px}").radius(t.border_radius.button)
    s = s.font_weight(t.typography.medium).font_size(t.typography.sm)
    s = s.transition(t.transitions.color)

    if variant == "outline":
        s._props["border"] = f"1px solid {t.colors.border_strong}"

    return s


def input_style(state: str = "default") -> StyleBuilder:
    """Input field style."""
    t = theme_manager.theme
    border_color = {
        "default": t.colors.border,
        "focus": t.colors.border_focus,
        "error": t.colors.error,
        "disabled": t.colors.border,
    }[state]

    s = style().bg(t.colors.surface).color(t.colors.text_primary)
    s = s.padding(f"{t.spacing.sm} {t.spacing.md}").radius(t.border_radius.input)
    s = s._props.update({"border": f"1px solid {border_color}"}) or s
    s = s.font_size(t.typography.base).transition(t.transitions.color)
    return s


def badge_style(variant: str = "default") -> StyleBuilder:
    """Badge style."""
    t = theme_manager.theme
    colors = {
        "default": (t.colors.surface_variant, t.colors.text_secondary),
        "primary": (t.colors.primary, t.colors.primary_contrast),
        "success": (t.colors.success, t.colors.success_contrast),
        "warning": (t.colors.warning, t.colors.warning_contrast),
        "error": (t.colors.error, t.colors.error_contrast),
        "info": (t.colors.info, t.colors.info_contrast),
    }
    bg, fg = colors.get(variant, colors["default"])

    return (style()
        .bg(bg).color(fg)
        .padding(f"{t.spacing.xs} {t.spacing.sm}")
        .radius(t.border_radius.badge)
        .font_size(t.typography.xs)
        .font_weight(t.typography.medium)
    )