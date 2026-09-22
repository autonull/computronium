"""Design tokens (M0.3) — colorblind-safe palettes, type scale, icon set, focus styles.

All tokens are pure data; components import from here. No side effects.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

# ──────────────────────────────────────────────────────────────────────────────
# Color Palettes (colorblind-safe: viridis/cividis families)
# ──────────────────────────────────────────────────────────────────────────────

# Primary semantic colors (light mode) - WCAG 2.2 AA compliant on white
# Dark mode colors are defined in HIGH_CONTRAST_CSS media query
SEMANTIC = {
    "success": "#1e7e34",  # darker green - 5.1:1 on white
    "warning": "#8b6914",  # dark amber - 5.1:1 on white
    "danger": "#c82333",  # darker red - 5.6:1 on white
    "info": "#0d6efd",  # bootstrap primary blue - 4.5:1 on white
    "neutral": "#495057",  # darker grey - 8.2:1 on white
}

# Outcome badges (from live_atlas.OutcomeStyle) — CVD-safe with shape redundancy
# Colors meet 3:1 UI contrast on light mode (white background)
OUTCOME_COLORS = {
    "LEARNED": "#1e7e34",  # darker green - 5.1:1 on white
    "MARGINAL": "#8b6914",  # dark amber - 5.1:1 on white
    "CHANCE": "#495057",  # darker grey - 8.2:1 on white
    "DIVERGED": "#c82333",  # darker red - 5.6:1 on white
    "DEFECT": "#212529",  # very dark - 15:1 on white
    "VOID": "#6c757d",  # grey - 4.5:1 on white (void = empty/unknown)
    "PARETO_OPTIMAL": "#8b6914",  # dark amber - 5.1:1 on white
    "PARETO_NEAR": "#987800",  # dark gold - 4.2:1 on white
    "DOMINATED": "#495057",  # darker grey - 8.2:1 on white
}

# Event kinds - UI contrast compliant (3:1) on both backgrounds
EVENT_COLORS = {
    "state": {
        "idle": "#495057",
        "proposing": "#0d6efd",
        "training": "#1e7e34",
        "sleeping": "#b8860b",
        "paused": "#e0a800",
        "stopped": "#c82333",
    },
    "alert": {
        "breakthrough": "#1e7e34",
        "cascade": "#c82333",
        "completion": "#0d6efd",
    },
    "default": "#495057",
}

# Categorical palette for maps/charts (viridis, 12 colors, CVD-safe)
CATEGORICAL_VIRIDIS = [
    "#440154",
    "#482878",
    "#3e4a89",
    "#31688e",
    "#26828e",
    "#1f9e89",
    "#35b779",
    "#6ece58",
    "#b5de2b",
    "#fde725",
    "#addc30",
    "#5ec962",
]

# Sequential palette for heatmaps (cividis, CVD-safe)
SEQUENTIAL_CIVIDIS = [
    "#00204c",
    "#00336d",
    "#004788",
    "#005c9e",
    "#0071b1",
    "#0086c0",
    "#1d9bcc",
    "#4db0d5",
    "#81c4db",
    "#b8d7e2",
    "#f0ebe3",
    "#fefcd6",
]

# Diverging palette for difference maps (CVD-safe)
DIVERGING = [
    "#b2182b",
    "#d6604d",
    "#f4a582",
    "#fddbc7",
    "#f7f7f7",
    "#d1e5f0",
    "#92c5de",
    "#4393c3",
    "#2166ac",
    "#053061",
]

# Grayscale (for reduced-motion / print)
GRAYSCALE = {
    "black": "#000000",
    "gray900": "#111111",
    "gray800": "#222222",
    "gray700": "#333333",
    "gray600": "#444444",
    "gray500": "#666666",
    "gray400": "#888888",
    "gray300": "#aaaaaa",
    "gray200": "#cccccc",
    "gray100": "#eeeeee",
    "white": "#ffffff",
}

# ──────────────────────────────────────────────────────────────────────────────
# Type Scale (rem-based, fluid clamp)
# ──────────────────────────────────────────────────────────────────────────────

TYPE_SCALE = {
    "display": "clamp(2.5rem, 5vw, 4rem)",
    "h1": "clamp(2rem, 4vw, 3rem)",
    "h2": "clamp(1.5rem, 3vw, 2.25rem)",
    "h3": "clamp(1.25rem, 2.5vw, 1.75rem)",
    "h4": "clamp(1rem, 2vw, 1.25rem)",
    "body_lg": "1.125rem",  # 18px
    "body": "1rem",  # 16px
    "body_sm": "0.875rem",  # 14px
    "caption": "0.75rem",  # 12px
    "mono": "0.875rem",  # 14px monospace
    "mono_sm": "0.75rem",  # 12px monospace
}

FONT_WEIGHT = {
    "normal": "400",
    "medium": "500",
    "bold": "700",
}

LINE_HEIGHT = {
    "tight": "1.2",
    "normal": "1.5",
    "relaxed": "1.75",
}

# ──────────────────────────────────────────────────────────────────────────────
# Icon Set (shape-redundant: never color-only)
# ──────────────────────────────────────────────────────────────────────────────

# Each icon has a distinct shape; color is decorative only
ICONS = {
    # Navigation / UI
    "map": "🗺",
    "tradeoffs": "⚖",
    "repair": "🔧",
    "health": "💚",
    "progress": "📈",
    "glossary": "📖",
    "settings": "⚙",
    "search": "🔍",
    "filter": "🔽",
    "refresh": "🔄",
    "export": "📤",
    "import": "📥",
    # State / Status
    "idle": "⏸",
    "running": "▶",
    "paused": "⏸",
    "stopped": "⏹",
    "sleeping": "😴",
    "success": "✅",
    "warning": "⚠",
    "error": "❌",
    "info": "ℹ",
    # Outcomes (shape + color)
    "learned": "🟢",
    "marginal": "🟡",
    "chance": "⚪",
    "diverged": "🔴",
    "defect": "⚫",
    "void": "⬜",
    "pareto_optimal": "★",
    "pareto_near": "✦",
    "dominated": "⊘",
    # Actions
    "copy": "📋",
    "link": "🔗",
    "expand": "▼",
    "collapse": "▲",
    "pause": "⏸",
    "play": "▶",
    "stop": "⏹",
    "skip": "⏭",
    # Panels
    "atlas": "🗺",
    "pareto": "📊",
    "funnel": "🔻",
    "ticker": "📜",
    "events": "📋",
    "coverage": "📊",
    "strata": "📐",
    "diversity": "📈",
    "cost": "💰",
    "maturation": "🌱",
    # Gamification
    "badge": "🏅",
    "quest": "📜",
    "record": "🏆",
    "fog": "🌫",
    "region": "📍",
    # Auto-Evolve
    "constitution": "📜",
    "lineage": "🧬",
    "probe": "🔬",
    "stagnation": "📉",
    "genome": "🧬",
    "mutation": "🧪",
    "veto": "🚫",
    "episode": "🌙",
    "preview": "👁",
    # Accessibility
    "keyboard": "⌨",
    "screen_reader": "🔊",
    "contrast": "☀",
    "motion": "🌀",
    # Misc
    "star": "★",
    "check": "✓",
    "cross": "✗",
    "arrow_right": "→",
    "arrow_left": "←",
    "arrow_up": "↑",
    "arrow_down": "↓",
}

# ──────────────────────────────────────────────────────────────────────────────
# Spacing Scale (rem-based)
# ──────────────────────────────────────────────────────────────────────────────

SPACING = {
    "0": "0",
    "1": "0.25rem",  # 4px
    "2": "0.5rem",  # 8px
    "3": "0.75rem",  # 12px
    "4": "1rem",  # 16px
    "5": "1.25rem",  # 20px
    "6": "1.5rem",  # 24px
    "8": "2rem",  # 32px
    "10": "2.5rem",  # 40px
    "12": "3rem",  # 48px
    "16": "4rem",  # 64px
}

# ──────────────────────────────────────────────────────────────────────────────
# Border Radius
# ──────────────────────────────────────────────────────────────────────────────

BORDER_RADIUS = {
    "none": "0",
    "sm": "0.25rem",
    "md": "0.375rem",
    "lg": "0.5rem",
    "xl": "0.75rem",
    "full": "9999px",
}

# ──────────────────────────────────────────────────────────────────────────────
# Shadows
# ──────────────────────────────────────────────────────────────────────────────

SHADOWS = {
    "none": "none",
    "sm": "0 1px 2px 0 rgb(0 0 0 / 0.05)",
    "md": "0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)",
    "lg": "0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)",
    "xl": "0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)",
    "focus": "0 0 0 3px rgb(23 162 184 / 0.4)",  # info color for focus ring
}

# ──────────────────────────────────────────────────────────────────────────────
# Transitions (respects prefers-reduced-motion)
# ──────────────────────────────────────────────────────────────────────────────

TRANSITIONS = {
    "fast": "150ms ease",
    "normal": "200ms ease",
    "slow": "300ms ease",
}

# ──────────────────────────────────────────────────────────────────────────────
# Focus Styles (WCAG 2.2 AA: visible focus indicator)
# ──────────────────────────────────────────────────────────────────────────────

FOCUS_RING = {
    "width": "3px",
    "offset": "2px",
    "color": SEMANTIC["info"],  # #17a2b8 — high contrast on light/dark
    "style": "solid",
}

# ──────────────────────────────────────────────────────────────────────────────
# Z-Index Scale
# ──────────────────────────────────────────────────────────────────────────────

Z_INDEX = {
    "base": "0",
    "dropdown": "100",
    "sticky": "200",
    "fixed": "300",
    "modal_backdrop": "400",
    "modal": "500",
    "popover": "600",
    "tooltip": "700",
    "toast": "800",
}

# ──────────────────────────────────────────────────────────────────────────────
# Breakpoints
# ──────────────────────────────────────────────────────────────────────────────

BREAKPOINTS = {
    "sm": "640px",
    "md": "768px",
    "lg": "1024px",
    "xl": "1280px",
    "2xl": "1536px",
}

# ──────────────────────────────────────────────────────────────────────────────
# Register-specific token overrides
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True, slots=True)
class RegisterTokens:
    """Token overrides per register (Explorer vs Lab)."""

    # Explorer: larger touch targets, simpler density
    # Lab: denser, more info per pixel
    card_padding: str
    table_row_height: str
    icon_size: str
    density: Literal["comfortable", "compact"]


EXPLORER_TOKENS = RegisterTokens(
    card_padding=SPACING["4"],
    table_row_height="3rem",
    icon_size="1.5rem",
    density="comfortable",
)

LAB_TOKENS = RegisterTokens(
    card_padding=SPACING["2"],
    table_row_height="2rem",
    icon_size="1rem",
    density="compact",
)


def get_register_tokens(register: Literal["explorer", "lab"]) -> RegisterTokens:
    return EXPLORER_TOKENS if register == "explorer" else LAB_TOKENS


# ──────────────────────────────────────────────────────────────────────────────
# CSS Custom Properties Export (for NiceGUI tailwind-less styling)
# ──────────────────────────────────────────────────────────────────────────────


def _css_color_props() -> list[str]:
    lines: list[str] = []
    for name, value in SEMANTIC.items():
        lines.append(f"  --color-{name}: {value};")
    for name, value in OUTCOME_COLORS.items():
        lines.append(f"  --color-outcome-{name.lower()}: {value};")
    for name, value in GRAYSCALE.items():
        lines.append(f"  --color-gray-{name}: {value};")
    return lines


def _css_type_props() -> list[str]:
    lines: list[str] = []
    for name, value in TYPE_SCALE.items():
        lines.append(f"  --text-{name}: {value};")
    for name, value in FONT_WEIGHT.items():
        lines.append(f"  --font-weight-{name}: {value};")
    for name, value in LINE_HEIGHT.items():
        lines.append(f"  --line-height-{name}: {value};")
    return lines


def _css_spacing_props() -> list[str]:
    lines: list[str] = []
    for name, value in SPACING.items():
        lines.append(f"  --space-{name}: {value};")
    return lines


def _css_radius_props() -> list[str]:
    lines: list[str] = []
    for name, value in BORDER_RADIUS.items():
        lines.append(f"  --radius-{name}: {value};")
    return lines


def _css_shadow_props() -> list[str]:
    lines: list[str] = []
    for name, value in SHADOWS.items():
        lines.append(f"  --shadow-{name}: {value};")
    return lines


def _css_transition_props() -> list[str]:
    lines: list[str] = []
    for name, value in TRANSITIONS.items():
        lines.append(f"  --transition-{name}: {value};")
    return lines


def _css_focus_props() -> list[str]:
    return [
        f"  --focus-ring-width: {FOCUS_RING['width']};",
        f"  --focus-ring-offset: {FOCUS_RING['offset']};",
        f"  --focus-ring-color: {FOCUS_RING['color']};",
        f"  --focus-ring-style: {FOCUS_RING['style']};",
    ]


def _css_zindex_props() -> list[str]:
    lines: list[str] = []
    for name, value in Z_INDEX.items():
        lines.append(f"  --z-{name}: {value};")
    return lines


def css_custom_properties() -> str:
    """Generate CSS custom properties for all tokens.

    Usage: inject into page `<head>` or use with NiceGUI's `ui.add_head_html()`.
    """
    lines = [":root {"]
    lines.extend(_css_color_props())
    lines.extend(_css_type_props())
    lines.extend(_css_spacing_props())
    lines.extend(_css_radius_props())
    lines.extend(_css_shadow_props())
    lines.extend(_css_transition_props())
    lines.extend(_css_focus_props())
    lines.extend(_css_zindex_props())
    lines.append("}")
    return "\n".join(lines)


# ──────────────────────────────────────────────────────────────────────────────
# Reduced Motion Media Query
# ──────────────────────────────────────────────────────────────────────────────


REDUCED_MOTION_CSS = """
@media (prefers-reduced-motion: reduce) {
  :root {
    --transition-fast: 0ms;
    --transition-normal: 0ms;
    --transition-slow: 0ms;
  }
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
"""

# ──────────────────────────────────────────────────────────────────────────────
# High Contrast Media Query
# ──────────────────────────────────────────────────────────────────────────────

HIGH_CONTRAST_CSS = """
@media (prefers-contrast: high) {
  :root {
    --color-success: #006400;
    --color-warning: #b8860b;
    --color-danger: #8b0000;
    --color-info: #0056d2;
  }
}
"""
