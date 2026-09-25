"""Mode toggle — Explorer ⇄ Lab switch with localStorage persistence (M0.4).

Wires GlossaryService into all panels via a global register state.
"""

from __future__ import annotations

from collections.abc import Callable
from contextlib import suppress
from typing import Any, Literal

from nicegui import app, ui

from computronium.ui.glossary_service import (
    get_glossary_service,
    tr,
    tr_both,
)

# ──────────────────────────────────────────────────────────────────────────────
# Types
# ──────────────────────────────────────────────────────────────────────────────

Register = Literal["explorer", "lab"]
Callback = Callable[[Register], None]

_STORAGE_KEY = "computronium_ui_mode"


class _ModeState:
    """Current UI mode + change callbacks."""

    def __init__(self, register: Register) -> None:
        self._register: Register = register
        self._callbacks: list[Callback] = []

    @property
    def register(self) -> Register:
        return self._register

    def add_callback(self, cb: Callback) -> None:
        self._callbacks.append(cb)

    def notify(self, new_register: Register) -> None:
        self._register = new_register
        for cb in self._callbacks:
            cb(new_register)


# Module-level singleton state
_current_mode = _ModeState("explorer")


def get_mode() -> Register:
    """Current register."""
    return _current_mode.register


def set_mode(register: Register, persist: bool = True) -> None:
    """Switch register, notify all listeners, and publish ModeChanged on the bus."""
    if _current_mode.register == register:
        return
    _current_mode.notify(register)
    from computronium.ui.event_bus import ModeChanged, event_bus

    event_bus.publish(ModeChanged(mode=register))
    if persist:
        _persist(register)


def _persist(register: Register) -> None:
    """Persist to localStorage via NiceGUI's client storage."""
    with suppress(RuntimeError):
        app.storage.user[_STORAGE_KEY] = register


def _load_persisted() -> Register:
    """Load from localStorage, defaulting to 'explorer'."""
    try:
        value = app.storage.user.get(_STORAGE_KEY)
        if value in {"explorer", "lab"}:
            return value
    except RuntimeError:
        pass
    return "explorer"


def initialize_mode() -> None:
    """Call once at app startup to restore persisted mode."""
    register = _load_persisted()
    _current_mode._register = register
    _current_mode._callbacks.clear()
    # Apply to glossary service (singleton)
    get_glossary_service()  # ensure loaded


# ──────────────────────────────────────────────────────────────────────────────
# UI Component
# ──────────────────────────────────────────────────────────────────────────────


def mode_toggle_button(
    *,
    on_change: Callback | None = None,
    show_labels: bool = True,
) -> ui.element:
    """Render the Explorer/Lab toggle button.

    Args:
        on_change: Optional callback fired on mode change.
        show_labels: Whether to show "Explorer"/"Lab" text (Explorer mode)
                     or just icons (Lab mode).
    """
    if on_change:
        _current_mode.add_callback(on_change)

    with ui.row().classes("items-center gap-2") as container:
        # Explorer button
        explorer_btn = (
            ui
            .button(
                "🧭 Explorer" if show_labels else "🧭",
                on_click=lambda: _switch("explorer"),
            )
            .props("flat dense")
            .classes("transition-colors")
        )
        explorer_btn.tooltip("Plain language view")

        # Lab button
        lab_btn = (
            ui
            .button(
                "🔬 Lab" if show_labels else "🔬",
                on_click=lambda: _switch("lab"),
            )
            .props("flat dense")
            .classes("transition-colors")
        )
        lab_btn.tooltip("Technical precision view")

        # Visual indicator of active mode
        indicator = ui.label().classes("text-xs text-grey min-w-[4rem] text-center")

    def _switch(new_register: Register) -> None:
        set_mode(new_register)
        _update_ui(new_register)
        if on_change:
            on_change(new_register)

    def _update_ui(register: Register) -> None:
        if register == "explorer":
            explorer_btn.props("color=primary").classes(remove="text-grey")
            lab_btn.props("flat").classes(add="text-grey")
            indicator.set_text("Explorer")
        else:
            explorer_btn.props("flat").classes(add="text-grey")
            lab_btn.props("color=primary").classes(remove="text-grey")
            indicator.set_text("Lab")

    # Initial render
    _update_ui(get_mode())

    return container


def mode_toggle_select(
    *,
    on_change: Callback | None = None,
) -> ui.select:
    """Alternative: dropdown select for mode."""
    if on_change:
        _current_mode.add_callback(on_change)

    select = (
        ui
        .select(
            options={
                "explorer": "🧭 Explorer (plain language)",
                "lab": "🔬 Lab (technical)",
            },
            value=get_mode(),
            on_change=lambda e: _on_select(e.value),
        )
        .props("dense outlined")
        .classes("w-48")
    )

    def _on_select(value: str) -> None:
        register: Register = value  # type: ignore[assignment]
        set_mode(register)
        if on_change:
            on_change(register)

    return select


# ──────────────────────────────────────────────────────────────────────────────
# Glossary-aware component mixin
# ──────────────────────────────────────────────────────────────────────────────


class GlossaryAware:
    """Mixin for components that need register-aware strings.

    Usage:
        class MyPanel(GlossaryAware):
            def render(self):
                self.tr("pareto_optimal")  # "Best trade-off" or "Pareto optimal"
    """

    def __init__(self) -> None:
        self._register: Register = get_mode()
        _current_mode.add_callback(self._on_mode_change)

    def _on_mode_change(self, register: Register) -> None:
        self._register = register
        self._refresh()

    def _refresh(self) -> None:
        """Override in subclass to re-render on mode change."""

    def tr(self, key: str) -> str:
        """Translate key in current register."""
        return tr(key, self._register)

    def tr_both(self, key: str) -> tuple[str, str]:
        """Get both registers for a key."""
        return tr_both(key)

    @property
    def register(self) -> Register:
        return self._register

    @property
    def is_explorer(self) -> bool:
        return self._register == "explorer"

    @property
    def is_lab(self) -> bool:
        return self._register == "lab"


# ──────────────────────────────────────────────────────────────────────────────
# Panel base with "What am I looking at?" drawer (M1.3)
# ──────────────────────────────────────────────────────────────────────────────


class BasePanel(GlossaryAware):
    """Base class for all dashboard panels.

    Provides:
    - Register-aware strings via GlossaryAware
    - "What am I looking at?" drawer (plain → why → expert → docs link)
    - Consistent card styling
    """

    def __init__(
        self,
        panel_key: str,
        *,
        plain_explanation: str,
        why_explanation: str,
        expert_explanation: str,
        docs_url: str | None = None,
    ) -> None:
        super().__init__()
        self.panel_key = panel_key
        self.plain_explanation = plain_explanation
        self.why_explanation = why_explanation
        self.expert_explanation = expert_explanation
        self.docs_url = docs_url
        self._drawer: Any = None

    def render_header(
        self, title_key: str, *, actions: list[Callable[[], ui.element]] | None = None
    ) -> ui.element:
        """Render panel header with title, mode badge, and 'What am I looking at?' button."""
        with ui.row().classes("w-full items-center justify-between") as header:
            with ui.row().classes("items-center gap-2"):
                ui.label(self.tr(title_key)).classes("text-h4")
                # Mode badge
                badge_text = "Explorer" if self.is_explorer else "Lab"
                badge_color = "primary" if self.is_explorer else "secondary"
                ui.badge(badge_text, color=badge_color).props("outline").classes(
                    "text-xs"
                )

            with ui.row().classes("items-center gap-2"):
                if actions:
                    for action_factory in actions:
                        action_factory()
                # "What am I looking at?" button
                ui.button(
                    self.tr("what_am_i_looking_at"),
                    icon="help_outline",
                    on_click=self._open_drawer,
                ).props("flat dense").classes("text-sm")

        return header

    def _open_drawer(self) -> None:
        """Open the explanatory drawer."""
        if self._drawer is None:
            self._create_drawer()
        if self._drawer is not None:
            self._drawer.open()

    def _create_drawer(self) -> None:
        """Create the 'What am I looking at?' drawer."""
        self._drawer = ui.right_drawer(value=False).props("width=480")
        with self._drawer:
            with ui.card().classes("w-full p-4"):
                ui.label(self.tr("what_am_i_looking_at")).classes("text-h6 mb-4")

            # Plain language
            with ui.expansion(self.tr("plain_language"), value=True).classes("w-full"):
                ui.label(self.plain_explanation).classes("text-body")

            # Why this matters
            with ui.expansion(self.tr("why_this_matters"), value=False).classes(
                "w-full"
            ):
                ui.label(self.why_explanation).classes("text-body")

            # Expert detail
            with ui.expansion(self.tr("expert_detail"), value=False).classes("w-full"):
                ui.label(self.expert_explanation).classes("text-body font-mono text-xs")

            # Docs link
            if self.docs_url:
                ui.separator().classes("my-2")
                ui.link("Read the full documentation", self.docs_url).props(
                    "target=_blank"
                ).classes("text-primary")

    # Subclasses must implement
    def render(self) -> ui.element:
        raise NotImplementedError

    def update_data(self, data: object | None = None, **kwargs: object) -> None:
        """Push fresh data into the panel; no-op by default.

        Data-driven panels override this, accepting the panel's typed data
        object positionally plus component-specific keyword arguments.
        """

    def on_mount(self) -> None:
        """First render into a live container."""

    def on_data_update(self, data: object | None = None) -> None:
        """Fresh data was pushed via ``update_data``."""

    def on_visibility_change(self, visible: bool) -> None:
        """Container shown or hidden by view/tab navigation."""

    def on_unmount(self) -> None:
        """Container discarded (e.g. campaign root switch)."""
