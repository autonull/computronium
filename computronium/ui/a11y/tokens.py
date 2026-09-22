"""Accessibility design tokens (M0.3) — contrast, motion, focus.

WCAG 2.2 AA compliant tokens for accessible UI.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

# ──────────────────────────────────────────────────────────────────────────────
# Contrast Ratios (WCAG 2.2 AA)
# ──────────────────────────────────────────────────────────────────────────────

# Minimum contrast ratios
MIN_CONTRAST_AA_NORMAL = 4.5  # Normal text (≥18px or ≥14px bold)
MIN_CONTRAST_AA_LARGE = 3.0  # Large text (≥18px or ≥14px bold)
MIN_CONTRAST_AAA_NORMAL = 7.0  # Enhanced
MIN_CONTRAST_AAA_LARGE = 4.5  # Enhanced large

# UI component contrast (non-text)
MIN_CONTRAST_UI = 3.0  # Borders, icons, focus indicators

# ──────────────────────────────────────────────────────────────────────────────
# Color Contrast Validation
# ──────────────────────────────────────────────────────────────────────────────


def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    """Convert hex color to RGB tuple."""
    hex_color = hex_color.lstrip("#")
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return (r, g, b)


def relative_luminance(rgb: tuple[int, int, int]) -> float:
    """Calculate relative luminance per WCAG."""

    def channel(c: int) -> float:
        c_norm = c / 255.0
        return (
            c_norm / 12.92 if c_norm <= 0.03928 else ((c_norm + 0.055) / 1.055) ** 2.4
        )

    r, g, b = (channel(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(fg: str, bg: str) -> float:
    """Calculate contrast ratio between two hex colors."""
    l1 = relative_luminance(hex_to_rgb(fg))
    l2 = relative_luminance(hex_to_rgb(bg))
    lighter = max(l1, l2)
    darker = min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


def meets_aa(fg: str, bg: str, large_text: bool = False) -> bool:
    """Check if color pair meets WCAG AA."""
    required = MIN_CONTRAST_AA_LARGE if large_text else MIN_CONTRAST_AA_NORMAL
    return contrast_ratio(fg, bg) >= required


def meets_aaa(fg: str, bg: str, large_text: bool = False) -> bool:
    """Check if color pair meets WCAG AAA."""
    required = MIN_CONTRAST_AAA_LARGE if large_text else MIN_CONTRAST_AAA_NORMAL
    return contrast_ratio(fg, bg) >= required


def meets_ui(fg: str, bg: str) -> bool:
    """Check if color pair meets UI component contrast (3:1)."""
    return contrast_ratio(fg, bg) >= MIN_CONTRAST_UI


# ──────────────────────────────────────────────────────────────────────────────
# Focus Indicator Tokens
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True, slots=True)
class FocusStyle:
    """Focus indicator style meeting WCAG 2.2 AA 2.4.7 & 2.4.11."""

    outline_width: str = "3px"
    outline_style: str = "solid"
    outline_offset: str = "2px"
    outline_color: str = "#0d6efd"  # SEMANTIC["info"] - high contrast on light/dark
    box_shadow: str = (
        "0 0 0 3px #0d6efd"  # Fallback for elements where outline doesn't work
    )


FOCUS_DEFAULT = FocusStyle()

FOCUS_HIGH_CONTRAST = FocusStyle(
    outline_width="4px",
    outline_color="#000000",
    box_shadow="0 0 0 4px #000000",
)

FOCUS_WHITE_ON_DARK = FocusStyle(
    outline_color="#ffffff",
    box_shadow="0 0 0 3px #ffffff",
)


# ──────────────────────────────────────────────────────────────────────────────
# Motion Tokens (respects prefers-reduced-motion)
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True, slots=True)
class MotionTokens:
    """Animation/motion tokens respecting prefers-reduced-motion."""

    # Normal durations
    fast: str = "150ms"
    normal: str = "200ms"
    slow: str = "300ms"

    # Easing
    ease: str = "ease"
    ease_out: str = "ease-out"
    ease_in_out: str = "ease-in-out"

    # Reduced motion overrides (applied via @media query)
    reduced_fast: str = "0ms"
    reduced_normal: str = "0ms"
    reduced_slow: str = "0ms"


MOTION = MotionTokens()


# ──────────────────────────────────────────────────────────────────────────────
# Touch Target Sizes (WCAG 2.5.5 Target Size)
# ──────────────────────────────────────────────────────────────────────────────

# Minimum touch target: 44×44 CSS pixels (AA)
# Recommended: 48×48 dp (Material) / 44×44 pt (iOS)
MIN_TOUCH_TARGET = "44px"
RECOMMENDED_TOUCH_TARGET = "48px"

# Spacing between touch targets
TOUCH_TARGET_GAP = "8px"


# ──────────────────────────────────────────────────────────────────────────────
# Text Spacing (WCAG 1.4.12 Text Spacing)
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True, slots=True)
class TextSpacing:
    """Text spacing metrics for readability."""

    line_height: float = 1.5  # ≥1.5x font size
    paragraph_spacing: float = 2.0  # ≥2x font size
    letter_spacing: float = 0.12  # ≥0.12x font size
    word_spacing: float = 0.16  # ≥0.16x font size


TEXT_SPACING = TextSpacing()


# ──────────────────────────────────────────────────────────────────────────────
# ARIA Live Region Tokens
# ──────────────────────────────────────────────────────────────────────────────

LivePoliteness = Literal["off", "polite", "assertive"]


@dataclass(frozen=True, slots=True)
class LiveRegionConfig:
    """Configuration for aria-live regions."""

    politeness: LivePoliteness = "polite"
    atomic: bool = True
    relevant: str = "additions text"
    # Rate limiting for polite regions
    min_interval_ms: int = 500  # Max 1 announcement per 500ms


LIVE_REGION_CONFIG = LiveRegionConfig()


# ──────────────────────────────────────────────────────────────────────────────
# Skip Link
# ──────────────────────────────────────────────────────────────────────────────

SKIP_LINK_CSS = """
/* Skip to main content link - WCAG 2.4.1 */
.skip-link {
  position: absolute;
  top: -100%;
  left: 50%;
  transform: translateX(-50%);
  background: #000;
  color: #fff;
  padding: 0.75rem 1.5rem;
  z-index: 10000;
  text-decoration: none;
  font-weight: 600;
  border-radius: 0 0 0.5rem 0.5rem;
}
.skip-link:focus {
  top: 0;
  outline: 3px solid #0d6efd;
  outline-offset: 2px;
}
"""


# ──────────────────────────────────────────────────────────────────────────────
# Screen Reader Only
# ──────────────────────────────────────────────────────────────────────────────

SR_ONLY_CSS = """
/* Visually hidden but screen reader accessible */
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}
"""


# ──────────────────────────────────────────────────────────────────────────────
# Focus Visible Polyfill (for older browsers)
# ──────────────────────────────────────────────────────────────────────────────

FOCUS_VISIBLE_CSS = """
/* :focus-visible polyfill behavior */
:focus:not(:focus-visible) {
  outline: none;
}
:focus-visible {
  outline: var(--focus-ring-width, 3px) solid var(--focus-ring-color, #0d6efd);
  outline-offset: var(--focus-ring-offset, 2px);
}
"""


# ──────────────────────────────────────────────────────────────────────────────
# Combined A11y CSS
# ──────────────────────────────────────────────────────────────────────────────


def a11y_css() -> str:
    """Generate combined accessibility CSS."""
    return "\n".join([
        SKIP_LINK_CSS,
        SR_ONLY_CSS,
        FOCUS_VISIBLE_CSS,
        "",
        "/* Reduced motion */",
        "@media (prefers-reduced-motion: reduce) {",
        "  *, *::before, *::after {",
        "    animation-duration: 0.01ms !important;",
        "    animation-iteration-count: 1 !important;",
        "    transition-duration: 0.01ms !important;",
        "    scroll-behavior: auto !important;",
        "  }",
        "}",
        "",
        "/* High contrast */",
        "@media (prefers-contrast: high) {",
        "  :root {",
        "    --color-success: #006400;",
        "    --color-warning: #b8860b;",
        "    --color-danger: #8b0000;",
        "    --color-info: #0056d2;",
        "  }",
        "}",
    ])
