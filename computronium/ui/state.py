"""Reactive State Management — signals, derived state, and subscriptions.

Provides a lightweight reactive system inspired by SolidJS/Svelte:
- `signal()` — mutable reactive values
- `computed()` — derived state that auto-updates
- `effect()` — side effects that track dependencies
- `batch()` — batch multiple updates
"""

from __future__ import annotations

import asyncio
from contextlib import suppress
from dataclasses import dataclass, field
from typing import Any, Callable, Generic, Literal, TypeVar

T = TypeVar("T")

FilterOutcome = Literal["any", "pareto", "dominated", "diverged", "defect"]
FilterMaturity = Literal["any", "l0", "l1", "l2"]


@dataclass(frozen=True, slots=True)
class AtlasFilters:
    """Structured Atlas filter state (§4.2) — the interaction-state layer's job.

    Empty facet sets mean "no constraint". Facets cover the axes the KB
    records per cell (D/C/U/topology); substrate/plasticity facets wait on
    per-cell KB fields. ``maturity`` is ``None``-tolerant: rows with unknown
    maturity ignore that facet instead of vanishing.
    """

    dynamics: frozenset[str] = frozenset()
    credit: frozenset[str] = frozenset()
    update: frozenset[str] = frozenset()
    topology: frozenset[str] = frozenset()
    outcome: FilterOutcome = "any"
    maturity: FilterMaturity = "any"
    query: str = ""

    @property
    def active(self) -> bool:
        """Whether any facet constrains the visible cell set."""
        return bool(
            self.dynamics
            or self.credit
            or self.update
            or self.topology
            or self.outcome != "any"
            or self.maturity != "any"
            or self.query.strip()
        )

    def matches(
        self,
        *,
        key: str,
        dynamics: str,
        credit: str,
        update: str,
        topology: str,
        is_pareto: bool = False,
        is_nan: bool = False,
        is_defect: bool = False,
        maturity: str | None = None,
    ) -> bool:
        """Pure predicate: does one cell survive these filters?"""
        facets = (
            (self.dynamics, dynamics),
            (self.credit, credit),
            (self.update, update),
            (self.topology, topology),
        )
        if any(picked and value not in picked for picked, value in facets):
            return False
        if not self._outcome_ok(is_pareto, is_nan, is_defect):
            return False
        if (
            self.maturity != "any"
            and maturity is not None
            and maturity != self.maturity
        ):
            return False
        needle = self.query.strip().lower()
        return not needle or needle in key.lower()

    def _outcome_ok(self, is_pareto: bool, is_nan: bool, is_defect: bool) -> bool:
        """Outcome facet: dominated excludes front and diverged cells."""
        match self.outcome:
            case "any":
                return True
            case "pareto":
                return is_pareto
            case "dominated":
                return not is_pareto and not is_nan
            case "diverged":
                return is_nan
            case "defect":
                return is_defect


@dataclass
class Signal(Generic[T]):
    """Reactive signal — mutable value with change notification."""

    value: T
    _subscribers: set[Callable[[T], None]] = field(default_factory=set, repr=False)
    _version: int = 0

    def get(self) -> T:
        """Get value and track dependency if in effect."""
        _track(self)
        return self.value

    def set(self, new_value: T | Callable[[T], T]) -> None:
        """Set value and notify subscribers."""
        if callable(new_value):
            new_value = new_value(self.value)
        if new_value != self.value:
            self.value = new_value
            self._version += 1
            for sub in self._subscribers:
                with suppress(Exception):
                    sub(new_value)

    def subscribe(self, callback: Callable[[T], None]) -> Callable[[], None]:
        """Subscribe to changes."""
        self._subscribers.add(callback)
        return lambda: self._subscribers.discard(callback)

    def peek(self) -> T:
        """Get value without tracking."""
        return self.value


@dataclass
class Computed(Generic[T]):
    """Derived state — recomputes when dependencies change."""

    _fn: Callable[[], T]
    _value: T | None = None
    _subscribers: set[Callable[[T], None]] = field(default_factory=set, repr=False)
    _dirty: bool = True
    _dependencies: set[Signal] = field(default_factory=set)

    def get(self) -> T:
        """Get value, recomputing if dirty."""
        _track(self)
        if self._dirty:
            _COMPUTED_STACK.append(self)
            self._dependencies.clear()
            try:
                self._value = self._fn()
            finally:
                _COMPUTED_STACK.pop()
            self._dirty = False
            for sub in self._subscribers:
                with suppress(Exception):
                    sub(self._value)
        return self._value  # type: ignore[return-value]

    def subscribe(self, callback: Callable[[T], None]) -> Callable[[], None]:
        self._subscribers.add(callback)
        return lambda: self._subscribers.discard(callback)

    def invalidate(self) -> None:
        """Mark as dirty (called when dependency changes)."""
        if not self._dirty:
            self._dirty = True
            for sub in self._subscribers:
                with suppress(Exception):
                    sub(self._value)  # Notify with stale value, they'll re-read


@dataclass
class Effect:
    """Side effect that auto-tracks signal dependencies."""

    _fn: Callable[[], Any | Callable[[], None]]
    _cleanup: Callable[[], None] | None = None
    _dependencies: set[Signal | Computed] = field(default_factory=set)
    _active: bool = True

    def __post_init__(self):
        _run_effect(self)

    def dispose(self) -> None:
        """Stop effect and run cleanup."""
        self._active = False
        if self._cleanup:
            with suppress(Exception):
                self._cleanup()
        for dep in self._dependencies:
            dep._subscribers.discard(self._invalidate)
        self._dependencies.clear()

    def _invalidate(self) -> None:
        if self._active:
            asyncio.create_task(_rerun_effect(self))

    def _rerun(self) -> None:
        if self._cleanup:
            with suppress(Exception):
                self._cleanup()
        _run_effect(self)


# ──────────────────────────────────────────────────────────────────────────────
# Dependency Tracking
# ──────────────────────────────────────────────────────────────────────────────

_COMPUTED_STACK: list[Computed] = []
_EFFECT_STACK: list[Effect] = []


def _track(observable: Signal | Computed) -> None:
    """Register current computed/effect as dependent on observable."""
    if _COMPUTED_STACK:
        current = _COMPUTED_STACK[-1]
        current._dependencies.add(observable)
        if isinstance(observable, Signal):
            observable._subscribers.add(current.invalidate)
        else:
            observable._subscribers.add(current.invalidate)
    elif _EFFECT_STACK:
        current = _EFFECT_STACK[-1]
        current._dependencies.add(observable)
        if isinstance(observable, Signal):
            observable._subscribers.add(current._invalidate)
        else:
            observable._subscribers.add(current._invalidate)


def _run_effect(effect: Effect) -> None:
    _EFFECT_STACK.append(effect)
    try:
        result = effect._fn()
        if callable(result):
            effect._cleanup = result
    finally:
        _EFFECT_STACK.pop()


async def _rerun_effect(effect: Effect) -> None:
    # Debounce rapid invalidations
    await asyncio.sleep(0)
    if effect._active:
        effect._rerun()


# ──────────────────────────────────────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────────────────────────────────────


def signal(initial: T) -> Signal[T]:
    """Create a reactive signal."""
    return Signal(initial)


def computed(fn: Callable[[], T]) -> Computed[T]:
    """Create a derived signal."""
    return Computed(fn)


def effect(fn: Callable[[], Any | Callable[[], None]]) -> Effect:
    """Create a reactive effect."""
    return Effect(fn)


def batch(fn: Callable[[], None]) -> None:
    """Batch multiple signal updates into single notification."""
    # Simple implementation: just run synchronously
    # In production, could defer notifications
    fn()


def untracked(fn: Callable[[], T]) -> T:
    """Run function without tracking dependencies."""
    return fn()


# ──────────────────────────────────────────────────────────────────────────────
# Store Pattern — Global Reactive State
# ──────────────────────────────────────────────────────────────────────────────


class Store:
    """Global reactive store with namespaced signals."""

    def __init__(self) -> None:
        self._signals: dict[str, Signal] = {}

    def get(self, key: str, default: T | None = None) -> Signal[T]:
        """Get or create a signal."""
        if key not in self._signals:
            self._signals[key] = signal(default)
        return self._signals[key]

    def set(self, key: str, value: T) -> None:
        """Set signal value."""
        self.get(key).set(value)

    def delete(self, key: str) -> None:
        """Remove a signal."""
        self._signals.pop(key, None)

    def clear(self) -> None:
        """Clear all signals."""
        self._signals.clear()


# Global stores
ui_store = Store()  # UI state (modals, toasts, loading)
data_store = Store()  # Data state (snapshots, filters)
session_store = Store()  # Session state (user, preferences)

# Cross-panel interaction state (GAME.todo7 Invariant 2) — selection,
# filters, density, scrub cursor. Panels never do I/O and never poll;
# this is the only push state in the dashboard.
selected_cell_key: Signal[str | None] = signal(None)
atlas_filters: Signal[AtlasFilters] = signal(AtlasFilters())
