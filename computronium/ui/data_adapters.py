"""Data Adapter Protocol (X2) — pure adapters from DashboardSnapshot to panel data.

Each panel declares its adapter; DashboardApp calls adapter before render.
Pure, testable, swappable; enables stub adapters for UI tests.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Protocol, TypeVar

if TYPE_CHECKING:
    from pathlib import Path

    from computronium.visualization.live_atlas import DashboardSnapshot

PanelDataT = TypeVar("PanelDataT", covariant=True)


class DataAdapter(Protocol[PanelDataT]):
    """Protocol for adapting a DashboardSnapshot to panel-specific data.

    Adapters are pure functions — no I/O, no side effects.
    They transform the raw snapshot into the typed dataclass the panel expects.
    """

    def adapt(self, snapshot: DashboardSnapshot, root: Path) -> PanelDataT:
        """Convert snapshot to panel data.

        Args:
            snapshot: The full dashboard snapshot from render_snapshot().
            root: The campaign root path (for any additional artifact reads).

        Returns:
            Typed data for the panel.
        """
        ...


@dataclass(frozen=True, slots=True)
class AdapterContext:
    """Context passed to adapters for additional artifact access."""

    root: Path
    snapshot: DashboardSnapshot


# Convenience function type for simple adapters
type AdapterFn[PanelDataT] = Callable[[DashboardSnapshot, Path], PanelDataT]


class FunctionAdapter[PanelDataT]:
    """Wrap a plain function as a DataAdapter."""

    def __init__(self, fn: AdapterFn[PanelDataT]) -> None:
        self._fn = fn

    def adapt(self, snapshot: DashboardSnapshot, root: Path) -> PanelDataT:
        return self._fn(snapshot, root)


def make_adapter[PanelDataT](fn: AdapterFn[PanelDataT]) -> DataAdapter[PanelDataT]:
    """Create a DataAdapter from a pure function."""
    return FunctionAdapter(fn)
