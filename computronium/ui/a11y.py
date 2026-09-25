"""Accessibility Utilities — ARIA, focus management, keyboard navigation.

Provides:
- ARIA attribute helpers
- Focus trap for modals/drawers
- Keyboard navigation helpers
- Live region management
- Screen reader announcements
- Reduced motion detection
"""

from __future__ import annotations

from contextlib import suppress
from dataclasses import dataclass, field
from typing import Any, Callable, Optional


# ──────────────────────────────────────────────────────────────────────────────
# ARIA Helpers
# ──────────────────────────────────────────────────────────────────────────────

def aria(**attrs: str | bool | int | None) -> dict[str, str]:
    """Build ARIA attributes dict, filtering None values.
    
    Usage:
        ui.button().props(aria(label="Close", expanded=False, controls="menu"))
    """
    result = {}
    for key, value in attrs.items():
        if value is not None:
            if isinstance(value, bool):
                result[f"aria-{key.replace('_', '-')}"] = "true" if value else "false"
            else:
                result[f"aria-{key.replace('_', '-')}"] = str(value)
    return result


def role(role_name: str) -> dict[str, str]:
    """Set ARIA role."""
    return {"role": role_name}


def live_region(politeness: str = "polite", atomic: bool = True) -> dict[str, str]:
    """Create live region attributes."""
    return aria(live=politeness, atomic=atomic)


def described_by(*ids: str) -> dict[str, str]:
    """Link to descriptive elements."""
    return {"aria-describedby": " ".join(ids)} if ids else {}


def labelled_by(*ids: str) -> dict[str, str]:
    """Link to labelling elements."""
    return {"aria-labelledby": " ".join(ids)} if ids else {}


def owns(*ids: str) -> dict[str, str]:
    """Indicate owned elements."""
    return {"aria-owns": " ".join(ids)} if ids else {}


def active_descendant(id_: str) -> dict[str, str]:
    """Set active descendant for composite widgets."""
    return {"aria-activedescendant": id_}


# ──────────────────────────────────────────────────────────────────────────────
# Focus Management
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class FocusTrap:
    """Trap focus within a container (for modals, drawers)."""
    
    container: Any
    _previous_focus: Any = None
    _active: bool = False
    _handlers: list[Callable] = field(default_factory=list)

    def activate(self) -> None:
        """Activate focus trap."""
        if self._active:
            return
        self._active = True
        
        # Save current focus
        try:
            self._previous_focus = self.container.client.page.document.activeElement
        except Exception:
            pass

        # Focus first focusable element
        self._focus_first()

        # Add keydown handler for Tab/Shift+Tab
        def on_keydown(e: Any) -> None:
            if e.key == "Tab":
                self._handle_tab(e.shiftKey)

        handler = self.container.on("keydown", on_keydown)
        self._handlers.append(handler)

    def deactivate(self) -> None:
        """Deactivate focus trap and restore previous focus."""
        if not self._active:
            return
        self._active = False
        
        for handler in self._handlers:
            with suppress(Exception):
                handler.delete()
        self._handlers.clear()

        # Restore previous focus
        if self._previous_focus:
            with suppress(Exception):
                self._previous_focus.focus()

    def _focus_first(self) -> None:
        """Focus first focusable element in container."""
        focusable = self.container.querySelectorAll(
            'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        )
        if focusable.length > 0:
            with suppress(Exception):
                focusable[0].focus()

    def _focus_last(self) -> None:
        """Focus last focusable element in container."""
        focusable = self.container.querySelectorAll(
            'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        )
        if focusable.length > 0:
            with suppress(Exception):
                focusable[focusable.length - 1].focus()

    def _handle_tab(self, shift_key: bool) -> None:
        """Handle Tab/Shift+Tab to cycle focus."""
        focusable = self.container.querySelectorAll(
            'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        )
        if focusable.length <= 1:
            return

        try:
            active = self.container.client.page.document.activeElement
            idx = -1
            for i in range(focusable.length):
                if focusable[i] == active:
                    idx = i
                    break
            
            if shift_key:
                next_idx = (idx - 1) % focusable.length
            else:
                next_idx = (idx + 1) % focusable.length
            
            focusable[next_idx].focus()
        except Exception:
            pass


def trap_focus(container: Any) -> FocusTrap:
    """Create and activate a focus trap."""
    trap = FocusTrap(container)
    trap.activate()
    return trap


def focus_first(container: Any) -> None:
    """Focus first focusable element."""
    trap = FocusTrap(container)
    trap._focus_first()


def focus_last(container: Any) -> None:
    """Focus last focusable element."""
    trap = FocusTrap(container)
    trap._focus_last()


# ──────────────────────────────────────────────────────────────────────────────
# Keyboard Navigation
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class KeyboardHandler:
    """Handle keyboard navigation for composite widgets."""
    
    container: Any
    items_selector: str
    orientation: str = "vertical"  # "vertical" | "horizontal" | "both"
    loop: bool = True
    _handlers: list[Callable] = field(default_factory=list)
    _current_index: int = -1

    def __post_init__(self):
        self._bind_keys()

    def _bind_keys(self) -> None:
        """Bind keyboard events."""
        def on_keydown(e: Any) -> None:
            key = e.key
            
            if self.orientation in ("vertical", "both") and key in ("ArrowDown", "ArrowUp"):
                e.preventDefault()
                delta = 1 if key == "ArrowDown" else -1
                self._navigate(delta)
            elif self.orientation in ("horizontal", "both") and key in ("ArrowRight", "ArrowLeft"):
                e.preventDefault()
                delta = 1 if key == "ArrowRight" else -1
                self._navigate(delta)
            elif key == "Home":
                e.preventDefault()
                self._navigate_to(0)
            elif key == "End":
                e.preventDefault()
                self._navigate_to(-1)
            elif key in ("Enter", " "):
                self._activate_current()

        handler = self.container.on("keydown", on_keydown)
        self._handlers.append(handler)

    def _get_items(self) -> list[Any]:
        """Get focusable items."""
        return list(self.container.querySelectorAll(self.items_selector))

    def _navigate(self, delta: int) -> None:
        """Navigate by delta."""
        items = self._get_items()
        if not items:
            return
        
        if self._current_index == -1:
            self._current_index = 0 if delta > 0 else len(items) - 1
        else:
            self._current_index = (self._current_index + delta) % len(items)
        
        if self.loop or (0 <= self._current_index < len(items)):
            items[self._current_index].focus()

    def _navigate_to(self, index: int) -> None:
        """Navigate to specific index."""
        items = self._get_items()
        if not items:
            return
        
        if index == -1:
            index = len(items) - 1
        self._current_index = max(0, min(index, len(items) - 1))
        items[self._current_index].focus()

    def _activate_current(self) -> None:
        """Activate current item (Enter/Space)."""
        items = self._get_items()
        if 0 <= self._current_index < len(items):
            items[self._current_index].click()

    def dispose(self) -> None:
        """Remove handlers."""
        for handler in self._handlers:
            with suppress(Exception):
                handler.delete()
        self._handlers.clear()


def keyboard_nav(container: Any, items_selector: str, **kwargs) -> KeyboardHandler:
    """Create keyboard navigation handler."""
    return KeyboardHandler(container, items_selector, **kwargs)


# ──────────────────────────────────────────────────────────────────────────────
# Live Region / Screen Reader Announcements
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class LiveRegion:
    """ARIA live region for screen reader announcements."""
    
    element: Any
    politeness: str = "polite"  # "polite" | "assertive" | "off"

    def announce(self, message: str, clear_first: bool = True) -> None:
        """Announce message to screen readers."""
        if clear_first:
            self.element.set_text("")
        self.element.set_text(message)

    def clear(self) -> None:
        """Clear live region."""
        self.element.set_text("")


def create_live_region(politeness: str = "polite", container: Any = None) -> LiveRegion:
    """Create a live region element."""
    from nicegui import ui
    
    parent = container or ui.column().classes("sr-only")
    with parent:
        element = ui.element("div").props(
            f'aria-live="{politeness}" aria-atomic="true"'
        ).classes("sr-only")
    return LiveRegion(element, politeness)


# Global live regions
_polite_region: LiveRegion | None = None
_assertive_region: LiveRegion | None = None


def announce(message: str, politeness: str = "polite") -> None:
    """Global announcement function."""
    global _polite_region, _assertive_region
    
    if politeness == "assertive":
        if _assertive_region is None:
            _assertive_region = create_live_region("assertive")
        _assertive_region.announce(message)
    else:
        if _polite_region is None:
            _polite_region = create_live_region("polite")
        _polite_region.announce(message)


# ──────────────────────────────────────────────────────────────────────────────
# Reduced Motion
# ──────────────────────────────────────────────────────────────────────────────

def prefers_reduced_motion() -> bool:
    """Check if user prefers reduced motion."""
    try:
        from nicegui import ui
        return ui.run_javascript(
            "window.matchMedia('(prefers-reduced-motion: reduce)').matches"
        )
    except Exception:
        return False


def respect_motion(callback: Callable[[], None], fallback: Callable[[], None] | None = None) -> None:
    """Run callback only if reduced motion not preferred."""
    if not prefers_reduced_motion():
        callback()
    elif fallback:
        fallback()


# ──────────────────────────────────────────────────────────────────────────────
# Skip Link
# ──────────────────────────────────────────────────────────────────────────────

def skip_link(target_id: str, text: str = "Skip to main content") -> Any:
    """Create a skip link for keyboard users."""
    from nicegui import ui
    return (ui.link(text, f"#{target_id}")
        .classes("sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-50 focus:px-4 focus:py-2 focus:bg-primary focus:text-white focus:rounded")
        .props("aria-label='Skip to main content'"))


# ──────────────────────────────────────────────────────────────────────────────
# High Contrast
# ──────────────────────────────────────────────────────────────────────────────

def prefers_high_contrast() -> bool:
    """Check if user prefers high contrast."""
    try:
        from nicegui import ui
        return ui.run_javascript(
            "window.matchMedia('(prefers-contrast: high)').matches"
        )
    except Exception:
        return False