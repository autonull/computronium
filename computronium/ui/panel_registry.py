"""Panel Registry (X1) — typed registry for dashboard panels.

Panels self-register via `@panel_registry.register` decorator.
DashboardApp builds nav and panel map from registry.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Callable

    from computronium.ui.data_adapters import DataAdapter
    from computronium.ui.mode_toggle import BasePanel


@dataclass(frozen=True, slots=True)
class PanelSpec:
    """Specification for a registered panel."""

    key: str
    label_key: str
    icon: str
    factory: Callable[..., BasePanel]
    visible_predicate: Callable[[dict[str, Any]], bool] = field(default=lambda _: True)
    order: int = 0
    adapter: DataAdapter | None = field(default=None, repr=False)


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
        factory: Callable[..., BasePanel],
        *,
        visible_predicate: Callable[[dict[str, Any]], bool] | None = None,
        order: int | None = None,
        adapter: DataAdapter | None = None,
    ) -> Callable[..., BasePanel]:
        """Register a panel factory.

        Usage:
            @panel_registry.register("my_panel", "my_panel", "icon", MyPanel)
            class MyPanel(BasePanel): ...
        """
        if key in self._specs:
            raise ValueError(f"Panel already registered: {key}")

        spec = PanelSpec(
            key=key,
            label_key=label_key,
            icon=icon,
            factory=factory,
            visible_predicate=visible_predicate or (lambda _: True),
            order=order if order is not None else self._order_counter,
            adapter=adapter,
        )
        self._specs[key] = spec
        self._order_counter += 1
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
) -> Callable[[type[BasePanel]], type[BasePanel]]:
    """Class decorator to register a panel.

    Usage:
        @register_panel("my_panel", "my_panel", "icon")
        class MyPanel(BasePanel): ...
    """

    def decorator(cls: type[BasePanel]) -> type[BasePanel]:
        panel_registry.register(
            key=key,
            label_key=label_key,
            icon=icon,
            factory=cls,
            visible_predicate=visible_predicate,
            order=order,
            adapter=adapter,
        )
        return cls

    return decorator
