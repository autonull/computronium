"""Panel base — single-register `BasePanel` with the "What am I looking at?" drawer.

One register, progressive disclosure: panels carry plain-language labels
directly; depth lives in the drawer (plain → why → expert → docs).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from nicegui import ui

if TYPE_CHECKING:
    from collections.abc import Callable


class BasePanel:
    """Base class for all dashboard panels.

    Provides a plain-language header plus the "What am I looking at?"
    drawer (plain → why → expert → docs link) and the panel lifecycle
    hooks (`on_mount`, `on_data_update`, `on_visibility_change`,
    `on_unmount`) wired by `DashboardApp` on view/tab/root switches.
    """

    def __init__(
        self,
        panel_key: str,
        *,
        plain: str,
        why: str,
        expert: str,
        docs_url: str | None = None,
    ) -> None:
        self.panel_key = panel_key
        self.plain = plain
        self.why = why
        self.expert = expert
        self.docs_url = docs_url
        self._drawer: Any = None

    def render_header(
        self, title: str, *, actions: list[Callable[[], ui.element]] | None = None
    ) -> ui.element:
        """Render panel header with plain title and 'What am I looking at?' button."""
        with ui.row().classes("w-full items-center justify-between") as header:
            ui.label(title).classes("text-h4")

            with ui.row().classes("items-center gap-2"):
                if actions:
                    for action_factory in actions:
                        action_factory()
                ui.button(
                    "What am I looking at?",
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
                ui.label("What am I looking at?").classes("text-h6 mb-4")

            with ui.expansion("Plain language", value=True).classes("w-full"):
                ui.label(self.plain).classes("text-body")

            with ui.expansion("Why this matters", value=False).classes("w-full"):
                ui.label(self.why).classes("text-body")

            with ui.expansion("Expert detail", value=False).classes("w-full"):
                ui.label(self.expert).classes("text-body font-mono text-xs")

            if self.docs_url:
                ui.separator().classes("my-2")
                ui.link("Read the full documentation", self.docs_url).props(
                    "target=_blank"
                ).classes("text-primary")

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
