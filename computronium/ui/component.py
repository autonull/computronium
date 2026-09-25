"""Composable Component System — lifecycle, composition, and rendering.

Provides a React-like component model for NiceGUI with:
- Lifecycle hooks (on_mount, on_unmount, on_update)
- Declarative composition via `compose()`
- Automatic cleanup of subscriptions/timers
- Type-safe props and state
"""

from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from contextlib import suppress
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Callable, Generic, TypeVar

if TYPE_CHECKING:
    from nicegui import ui

T = TypeVar("T")
P = TypeVar("P")
S = TypeVar("S")


@dataclass(frozen=True, slots=True)
class ComponentProps(Generic[P]):
    """Immutable props passed to a component."""

    data: P


@dataclass
class ComponentState(Generic[S]):
    """Mutable state with change notification."""

    value: S
    _listeners: list[Callable[[S], None]] = field(default_factory=list, repr=False)

    def set(self, new_value: S) -> None:
        if new_value != self.value:
            self.value = new_value
            for listener in self._listeners:
                listener(new_value)

    def subscribe(self, listener: Callable[[S], None]) -> Callable[[], None]:
        self._listeners.append(listener)
        return lambda: self._listeners.remove(listener)


class LifecycleMixin:
    """Mixin providing lifecycle hooks for components."""

    def __init__(self) -> None:
        self._mounted = False
        self._cleanup_tasks: list[Callable[[], None]] = []
        self._timers: list[asyncio.TimerHandle] = []
        self._subscriptions: list[Callable[[], None]] = []

    def on_mount(self) -> None:
        """Called when component is first rendered."""
        pass

    def on_unmount(self) -> None:
        """Called when component is removed from UI."""
        pass

    def on_update(self, prev_props: Any, prev_state: Any) -> None:
        """Called when props or state change."""
        pass

    def _register_cleanup(self, cleanup: Callable[[], None]) -> None:
        """Register a cleanup function to run on unmount."""
        self._cleanup_tasks.append(cleanup)

    def _run_cleanup(self) -> None:
        """Run all registered cleanup functions."""
        for cleanup in self._cleanup_tasks:
            with suppress(Exception):
                cleanup()
        self._cleanup_tasks.clear()

    def set_timer(
        self, interval: float, callback: Callable[[], None], *, once: bool = False
    ) -> None:
        """Set a timer that's auto-cleaned on unmount."""
        loop = asyncio.get_event_loop()
        if once:
            handle = loop.call_later(interval, callback)
            self._register_cleanup(lambda: handle.cancel())
        else:

            async def _repeat():
                while True:
                    await asyncio.sleep(interval)
                    callback()

            task = asyncio.create_task(_repeat())
            self._register_cleanup(lambda: task.cancel())

    def subscribe(self, observable: Any, callback: Callable[[Any], None]) -> None:
        """Subscribe to an observable (event bus, store, etc.) with auto-cleanup."""
        unsubscribe = (
            observable.subscribe(callback)
            if hasattr(observable, "subscribe")
            else lambda: None
        )
        self._subscriptions.append(unsubscribe)
        self._register_cleanup(unsubscribe)


class Component(ABC, Generic[P, S], LifecycleMixin):
    """Base component class with props, state, and lifecycle.

    Usage:
        class MyComponent(Component[MyProps, MyState]):
            def initial_state(self) -> MyState: ...
            def render(self) -> ui.element: ...
    """

    def __init__(self, props: P | None = None) -> None:
        super().__init__()
        self.props = props
        self.state = self.initial_state()
        self._root: ui.element | None = None
        self._children: list[Component] = []

    @abstractmethod
    def initial_state(self) -> S:
        """Return initial state."""
        ...

    @abstractmethod
    def render(self) -> ui.element:
        """Render the component. Return root element."""
        ...

    def compose(self, *children: Component) -> list[Component]:
        """Declare child components. They'll be mounted/unmounted with parent."""
        self._children = list(children)
        return self._children

    def mount(self, parent: ui.element | None = None) -> ui.element:
        """Mount component into parent (or current context)."""
        if self._mounted:
            return self._root

        container = parent or ui.column().classes("w-full")
        with container:
            self._root = self.render()

        for child in self._children:
            child.mount(self._root)

        self._mounted = True
        self.on_mount()
        return self._root

    def unmount(self) -> None:
        """Unmount component and all children."""
        if not self._mounted:
            return

        for child in self._children:
            child.unmount()

        self.on_unmount()
        self._run_cleanup()
        self._mounted = False
        self._root = None

    def update_props(self, new_props: P) -> None:
        """Update props and trigger re-render."""
        prev_props = self.props
        self.props = new_props
        self._reconcile(prev_props, self.state)

    def set_state(self, new_state: S | Callable[[S], S]) -> None:
        """Update state and trigger re-render."""
        prev_state = self.state
        if callable(new_state):
            new_state = new_state(prev_state)
        self.state = new_state
        self._reconcile(self.props, prev_state)

    def _reconcile(self, prev_props: Any, prev_state: Any) -> None:
        """Re-render with new props/state. Override for custom diffing."""
        self.on_update(prev_props, prev_state)
        if self._root:
            self._root.clear()
            with self._root:
                self.render()
        for child in self._children:
            child._reconcile(prev_props, prev_state)


class StatelessComponent(Component[P, None]):
    """Component with no internal state."""

    def initial_state(self) -> None:
        return None


# ──────────────────────────────────────────────────────────────────────────────
# Composition Helpers
# ──────────────────────────────────────────────────────────────────────────────


def fragment(*elements: ui.element) -> list[ui.element]:
    """Return multiple elements without a wrapper (for use in render)."""
    return list(elements)


def conditional(
    condition: bool, true_elem: ui.element, false_elem: ui.element | None = None
) -> ui.element | None:
    """Conditional rendering."""
    return true_elem if condition else false_elem


def for_each(
    items: list[T], render_item: Callable[[T, int], ui.element]
) -> list[ui.element]:
    """Map items to elements."""
    return [render_item(item, i) for i, item in enumerate(items)]


# ──────────────────────────────────────────────────────────────────────────────
# Higher-Order Components
# ──────────────────────────────────────────────────────────────────────────────


def with_data(adapter_key: str) -> Callable[[type[Component]], type[Component]]:
    """HOC: Inject data adapter into component."""

    def decorator(component_cls: type[Component]) -> type[Component]:
        class WithData(component_cls):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self._adapter_key = adapter_key
                self._data = None

            def on_mount(self):
                super().on_mount()
                self._fetch_data()

            def _fetch_data(self):
                # Override in subclass or use adapter
                pass

        WithData.__name__ = f"WithData({component_cls.__name__})"
        return WithData

    return decorator


# ──────────────────────────────────────────────────────────────────────────────
# Component Registry
# ──────────────────────────────────────────────────────────────────────────────


class ComponentRegistry:
    """Registry for component factories with metadata."""

    def __init__(self) -> None:
        self._factories: dict[str, Callable[..., Component]] = {}
        self._metadata: dict[str, dict] = {}

    def register(
        self,
        key: str,
        factory: Callable[..., Component],
        *,
        label: str = "",
        icon: str = "",
        category: str = "general",
        description: str = "",
    ) -> None:
        self._factories[key] = factory
        self._metadata[key] = {
            "label": label,
            "icon": icon,
            "category": category,
            "description": description,
        }

    def create(self, key: str, *args, **kwargs) -> Component | None:
        factory = self._factories.get(key)
        if factory:
            return factory(*args, **kwargs)
        return None

    def get_metadata(self, key: str) -> dict | None:
        return self._metadata.get(key)

    def list_by_category(self, category: str) -> list[tuple[str, dict]]:
        return [(k, v) for k, v in self._metadata.items() if v["category"] == category]

    def all(self) -> list[tuple[str, dict]]:
        return list(self._metadata.items())


component_registry = ComponentRegistry()
