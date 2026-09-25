"""Accessibility package."""

from computronium.ui.a11y.audit import (
    AxeResult,
    AxeViolation,
    KeyboardCheckResult,
    ci_axe_scan,
    format_axe_report,
    has_critical_or_serious,
    run_axe_scan,
    run_keyboard_crawl,
    violations_by_severity,
)
from computronium.ui.a11y.tokens import (
    FOCUS_DEFAULT,
    FOCUS_HIGH_CONTRAST,
    FOCUS_WHITE_ON_DARK,
    LIVE_REGION_CONFIG,
    MIN_TOUCH_TARGET,
    MOTION,
    RECOMMENDED_TOUCH_TARGET,
    TEXT_SPACING,
    TOUCH_TARGET_GAP,
    a11y_css,
    contrast_ratio,
    meets_aa,
    meets_aaa,
    meets_ui,
)
# Import new utilities from the module file (not package) to avoid circular imports
import importlib.util
import sys

_spec = importlib.util.spec_from_file_location("a11y_module", "/home/me/computronium/computronium/ui/a11y.py")
_a11y_module = importlib.util.module_from_spec(_spec)
sys.modules["a11y_module"] = _a11y_module
_spec.loader.exec_module(_a11y_module)

aria = _a11y_module.aria
live_region = _a11y_module.live_region
described_by = _a11y_module.described_by
labelled_by = _a11y_module.labelled_by
owns = _a11y_module.owns
active_descendant = _a11y_module.active_descendant
role = _a11y_module.role
trap_focus = _a11y_module.trap_focus
focus_first = _a11y_module.focus_first
focus_last = _a11y_module.focus_last
keyboard_nav = _a11y_module.keyboard_nav
create_live_region = _a11y_module.create_live_region
announce = _a11y_module.announce
prefers_reduced_motion = _a11y_module.prefers_reduced_motion
respect_motion = _a11y_module.respect_motion
skip_link = _a11y_module.skip_link
prefers_high_contrast = _a11y_module.prefers_high_contrast

__all__ = [
    "FOCUS_DEFAULT",
    "FOCUS_HIGH_CONTRAST",
    "FOCUS_WHITE_ON_DARK",
    "LIVE_REGION_CONFIG",
    "MIN_TOUCH_TARGET",
    "MOTION",
    "RECOMMENDED_TOUCH_TARGET",
    "TEXT_SPACING",
    "TOUCH_TARGET_GAP",
    "AxeResult",
    "AxeViolation",
    "KeyboardCheckResult",
    "a11y_css",
    "ci_axe_scan",
    "contrast_ratio",
    "format_axe_report",
    "has_critical_or_serious",
    "meets_aa",
    "meets_aaa",
    "meets_ui",
    "run_axe_scan",
    "run_keyboard_crawl",
    "violations_by_severity",
    # New utilities
    "aria",
    "live_region",
    "described_by",
    "labelled_by",
    "owns",
    "active_descendant",
    "role",
    "trap_focus",
    "focus_first",
    "focus_last",
    "keyboard_nav",
    "create_live_region",
    "announce",
    "prefers_reduced_motion",
    "respect_motion",
    "skip_link",
    "prefers_high_contrast",
]