"""Panel Registry (X1) — typed registry for dashboard panels.

Panels self-register via `@panel_registry.register` decorator.
DashboardApp builds nav and panel map from registry.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Protocol

if TYPE_CHECKING:
    from nicegui import ui

    from computronium.ui.data_adapters import DataAdapter


type PanelFactory = Callable[..., PanelLike]


class PanelLike(Protocol):
    """Structural surface every registered panel must satisfy.

    ``update_data`` is duck-typed (data-driven panels override it with typed
    keyword arguments, so it can't be part of the structural contract).
    """

    def render(self) -> ui.element:
        """Render the panel."""
        ...

    def set_lens(self, lens: str) -> None:
        """Set active lens for panels that support lenses."""
        ...


@dataclass(frozen=True, slots=True)
class PanelSpec:
    """Specification for a registered panel."""

    key: str
    label_key: str
    icon: str
    factory: PanelFactory
    visible_predicate: Callable[[dict[str, Any]], bool] = field(default=lambda _: True)
    order: int = 0
    adapter: DataAdapter | None = field(default=None, repr=False)
    lenses: dict[str, str] = field(default_factory=dict)  # lens_key -> label
    default_lens: str | None = None


class PanelRegistry:
    """Central registry for dashboard panels."""

    def __init__(self) -> None:
        self._specs: dict[str, PanelSpec] = {}
        self._order_counter = 0

    def register(
        self,
        key: str,
        label_key: str,
        icon: str,
        factory: PanelFactory,
        *,
        visible_predicate: Callable[[dict[str, Any]], bool] | None = None,
        order: int | None = None,
        adapter: DataAdapter | None = None,
        lenses: dict[str, str] | None = None,
        default_lens: str | None = None,
    ) -> PanelFactory:
        """Register a panel factory; re-registration updates the existing spec
        in place (preserving its order unless overridden)."""
        spec = PanelSpec(
            key=key,
            label_key=label_key,
            icon=icon,
            factory=factory,
            visible_predicate=visible_predicate or (lambda _: True),
            order=(
                order
                if order is not None
                else self._specs[key].order
                if key in self._specs
                else self._order_counter
            ),
            adapter=adapter,
            lenses=lenses or {},
            default_lens=default_lens,
        )
        if key not in self._specs:
            self._order_counter += 1
        self._specs[key] = spec
        return factory

    def get(self, key: str) -> PanelSpec | None:
        """Get panel spec by key."""
        return self._specs.get(key)

    def all_specs(self) -> list[PanelSpec]:
        """Get all panel specs sorted by order."""
        return sorted(self._specs.values(), key=lambda s: s.order)

    def visible_specs(self, context: dict[str, Any]) -> list[PanelSpec]:
        """Get visible panel specs for the given context."""
        return [spec for spec in self.all_specs() if spec.visible_predicate(context)]

    def keys(self) -> list[str]:
        """Get all registered panel keys in order."""
        return [spec.key for spec in self.all_specs()]


# Global registry instance
panel_registry = PanelRegistry()


# Decorator for convenient registration
def register_panel(
    key: str,
    label_key: str,
    icon: str,
    *,
    visible_predicate: Callable[[dict[str, Any]], bool] | None = None,
    order: int | None = None,
    adapter: DataAdapter | None = None,
    lenses: dict[str, str] | None = None,
    default_lens: str | None = None,
) -> Callable[[type[PanelLike]], type[PanelLike]]:
    """Class decorator to register a panel.

    Usage:
        @register_panel("my_panel", "my_panel", "icon", lenses={"lens1": "Lens 1"})
        class MyPanel(BasePanel): ...
    """

    def decorator(cls: type[PanelLike]) -> type[PanelLike]:
        panel_registry.register(
            key=key,
            label_key=label_key,
            icon=icon,
            factory=cls,
            visible_predicate=visible_predicate,
            order=order,
            adapter=adapter,
            lenses=lenses,
            default_lens=default_lens,
        )
        return cls

    return decorator
