"""CellQuery adapter — single adapter producing CellView[] from DashboardSnapshot.

Lazy sub-loaders for evidence/figures/defects per visible row cap (1000).
Memoized per snapshot signature (tail-hash + EVENT_SCHEMA_VERSION).
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from pathlib import Path

    from computronium.visualization.live_atlas import DashboardSnapshot


@dataclass(frozen=True, slots=True)
class CellView:
    """A single cell view with all projections."""

    # 6-axis coordinate
    dynamics: str
    credit: str
    update: str
    topology: str
    substrate: str
    plasticity: str

    # Measurements
    accuracy: float
    bp_deficit: float
    walltime_s: float
    param_count: int
    flops: float
    memory_mb: float
    energy_per_step: float

    # Evidence (lazy-loaded)
    evidence_ref: str | None = None
    figure_ref: str | None = None

    # Defects (lazy-loaded)
    defect_ids: tuple[str, ...] = ()

    # Provenance
    campaign: str = ""
    seed: int = 0
    maturity: str = "l0"  # l0 | l1 | l2
    timestamp: float = 0.0

    # Defects
    is_void: bool = False
    is_nan: bool = False
    is_defect: bool = False

    # Figures
    figures: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class CellQueryResult:
    """Result of a CellQuery."""

    cells: list[CellView]
    total_count: int
    signature: str  # snapshot signature for memoization


class CellQuery:
    """Single adapter producing CellView[] from DashboardSnapshot + KB + CEEC ledger.

    Memoized per snapshot signature (tail-hash + EVENT_SCHEMA_VERSION).
    Lazy sub-loaders for evidence/figures/defects per visible row (cap 1000).
    """

    EVENT_SCHEMA_VERSION = "1"

    def __init__(self) -> None:
        self._cache: dict[str, CellQueryResult] = {}
        self._evidence_cache: dict[str, Any] = {}
        self._figure_cache: dict[str, Any] = {}
        self._defect_cache: dict[str, Any] = {}

    def _snapshot_signature(self, snapshot: DashboardSnapshot) -> str:
        """Compute snapshot signature for memoization."""
        # Tail hash of event history + schema version
        event_tail = (
            str(snapshot.event_history[-10:]) if snapshot.event_history else "empty"
        )
        tail_hash = hashlib.blake2b(event_tail.encode(), digest_size=8).hexdigest()
        return f"{self.EVENT_SCHEMA_VERSION}:{tail_hash}:{len(snapshot.event_history)}"

    def query(
        self,
        snapshot: DashboardSnapshot,
        root: Path,
        *,
        limit: int = 1000,
        offset: int = 0,
    ) -> CellQueryResult:
        """Query cells from snapshot with lazy sub-loaders."""
        sig = self._snapshot_signature(snapshot)

        if sig in self._cache:
            cached = self._cache[sig]
            # Apply pagination to cached result
            paginated = cached.cells[offset : offset + limit]
            return CellQueryResult(
                cells=paginated,
                total_count=cached.total_count,
                signature=sig,
            )

        # Build cells from snapshot data
        cells = self._build_cells(snapshot, root)
        total = len(cells)

        # Apply pagination
        paginated = cells[offset : offset + limit]

        result = CellQueryResult(cells=paginated, total_count=total, signature=sig)
        self._cache[sig] = result
        return result

    def _coerce_float(self, val: Any, default: float = 0.0) -> float:
        """Coerce value to float."""
        if val is None:
            return default
        if isinstance(val, int | float):
            return float(val)
        try:
            return float(val)
        except ValueError, TypeError:
            return default

    def _coerce_int(self, val: Any, default: int = 0) -> int:
        """Coerce value to int."""
        if val is None:
            return default
        if isinstance(val, int):
            return val
        if isinstance(val, float):
            return int(val)
        try:
            return int(val)
        except ValueError, TypeError:
            return default

    def _coerce_str(self, val: Any, default: str = "") -> str:
        """Coerce value to str."""
        if val is None:
            return default
        return str(val)

    def _coerce_bool(self, val: Any, default: bool = False) -> bool:
        """Coerce value to bool."""
        if val is None:
            return default
        if isinstance(val, bool):
            return val
        if isinstance(val, int | float):
            return bool(val)
        if isinstance(val, str):
            return val.lower() in {"true", "1", "yes"}
        return default

    def _build_cells(self, snapshot: DashboardSnapshot, root: Path) -> list[CellView]:
        """Build CellView list from snapshot."""
        from computronium.visualization.atlas import load_cells

        df = load_cells(root / "kb.sqlite")
        if df.empty:
            return []

        cells = []
        for _, row in df.iterrows():
            cell = CellView(
                dynamics=self._coerce_str(row.get("dynamics")),
                credit=self._coerce_str(row.get("credit")),
                update=self._coerce_str(row.get("update")),
                topology=self._coerce_str(row.get("topology"), "feedforward"),
                substrate=self._coerce_str(row.get("substrate"), "digital"),
                plasticity=self._coerce_str(row.get("plasticity"), "null"),
                accuracy=self._coerce_float(row.get("accuracy")),
                bp_deficit=self._coerce_float(row.get("bp_deficit")),
                walltime_s=self._coerce_float(row.get("walltime")),
                param_count=self._coerce_int(row.get("param_budget")),
                flops=self._coerce_float(row.get("flops")),
                memory_mb=self._coerce_float(row.get("memory_mb")),
                energy_per_step=self._coerce_float(row.get("energy_per_step")),
                campaign=self._coerce_str(row.get("campaign")),
                seed=self._coerce_int(row.get("seed")),
                maturity=self._coerce_str(row.get("maturity"), "l0"),
                timestamp=self._coerce_float(row.get("timestamp")),
                is_void=self._coerce_bool(row.get("is_void")),
                is_nan=self._coerce_bool(row.get("nan_loss")),
                is_defect=self._coerce_bool(row.get("is_defect")),
            )
            cells.append(cell)

        return cells

    def load_evidence(self, cell: CellView) -> Any:
        """Lazy-load evidence for a cell."""
        if cell.evidence_ref and cell.evidence_ref in self._evidence_cache:
            return self._evidence_cache[cell.evidence_ref]
        # Would load from CEEC ledger
        return None

    def load_figure(self, cell: CellView) -> Any:
        """Lazy-load figure for a cell."""
        if cell.figure_ref and cell.figure_ref in self._figure_cache:
            return self._figure_cache[cell.figure_ref]
        # Would load from figures store
        return None

    def load_defects(self, cell: CellView) -> tuple[str, ...]:
        """Lazy-load defects for a cell."""
        key = f"{cell.dynamics}|{cell.credit}|{cell.update}|{cell.topology}"
        if key in self._defect_cache:
            return self._defect_cache[key]
        # Would query defects
        return ()

    def clear_cache(self) -> None:
        """Clear all caches."""
        self._cache.clear()
        self._evidence_cache.clear()
        self._figure_cache.clear()
        self._defect_cache.clear()


# Global CellQuery instance
cell_query = CellQuery()


__all__ = [
    "CellQuery",
    "CellQueryResult",
    "CellView",
    "cell_query",
]
