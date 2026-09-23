"""Data Adapter Protocol (X2) — pure adapters from DashboardSnapshot to panel data.

Each panel declares its adapter; DashboardApp builds one AdapterContext per
refresh cycle and calls adapter.adapt(ctx). Adapters are pure, testable,
and swappable; enables stub adapters for UI tests.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Protocol, TypeVar

if TYPE_CHECKING:
    from pathlib import Path

    from computronium.ui.recognition.state_store import RecognitionStateStore
    from computronium.visualization.live_atlas import DashboardSnapshot

PanelDataT = TypeVar("PanelDataT", covariant=True)


@dataclass(frozen=True, slots=True)
class AdapterContext:
    """One refresh cycle's inputs to an adapter."""

    root: Path
    snapshot: DashboardSnapshot
    recognition_store: RecognitionStateStore | None = None


class DataAdapter(Protocol[PanelDataT]):
    """Protocol for adapting an AdapterContext to panel-specific data.

    Adapters are pure functions — no I/O, no side effects.
    They transform the raw snapshot into the typed dataclass the panel expects.
    """

    def adapt(self, ctx: AdapterContext) -> PanelDataT:
        """Convert the context to panel data.

        Args:
            ctx: Root path, full dashboard snapshot, optional recognition store.

        Returns:
            Typed data for the panel.
        """
        ...


# Convenience function type for simple adapters (snapshot, root unpacking)
type AdapterFn[PanelDataT] = Callable[[DashboardSnapshot, Path], PanelDataT]
type ContextAdapterFn[PanelDataT] = Callable[[AdapterContext], PanelDataT]


class FunctionAdapter[PanelDataT]:
    """Wrap a plain (snapshot, root) function as a DataAdapter."""

    def __init__(self, fn: AdapterFn[PanelDataT]) -> None:
        self._fn = fn

    def adapt(self, ctx: AdapterContext) -> PanelDataT:
        return self._fn(ctx.snapshot, ctx.root)


class ContextAdapter[PanelDataT]:
    """Wrap a context-aware function (needs recognition_store) as a DataAdapter."""

    def __init__(self, fn: ContextAdapterFn[PanelDataT]) -> None:
        self._fn = fn

    def adapt(self, ctx: AdapterContext) -> PanelDataT:
        return self._fn(ctx)


def make_adapter[PanelDataT](fn: AdapterFn[PanelDataT]) -> DataAdapter[PanelDataT]:
    """Create a DataAdapter from a pure (snapshot, root) function."""
    return FunctionAdapter(fn)


def make_context_adapter[PanelDataT](
    fn: ContextAdapterFn[PanelDataT],
) -> DataAdapter[PanelDataT]:
    """Create a DataAdapter from a full-context function."""
    return ContextAdapter(fn)
