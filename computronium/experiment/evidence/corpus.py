"""The corpus instrument: every readable evidence store, counted one way.

One implementation answers "what has the corpus exercised?" for both
``comp coverage report --corpus`` and ``scripts/probes/t3_credit_breadth.py``.
Two counters would drift; a lock compares the command's numbers with the
probe's.

Rulers: ``pass_cells`` counts PASS records (one per seed), not distinct
coordinates — the probe and the plan quote records. ``geometries[*].error_aware``
excludes credits that declare ``error_blind=True``: they read no label, so on a
supervised task they measure chance by contract and never count toward breadth.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from computronium.core.system_trainer.spec import _credit_from_config
from computronium.experiment.evidence.store import RecordStore, StoreConfig
from computronium.experiment.schema.axis import AXES_REGISTRIES, StructuralAxis
from computronium.experiment.schema.seed_registries import seed_all_registries
from computronium.ontology.credit import CreditAssignmentConfig

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping
    from pathlib import Path

__all__ = [
    "CorpusCoverage",
    "default_store_paths",
    "error_blind_credit",
    "scan_corpus",
]


def error_blind_credit(credit: str) -> bool:
    """Whether a credit declares that it reads no error signal."""
    factory = getattr(CreditAssignmentConfig, credit, None)
    if factory is None:
        return False
    return bool(_credit_from_config(factory()).error_blind)


def default_store_paths(root: Path) -> tuple[Path, ...]:
    """The stores the corpus instrument reads: ``experiments/*.duckdb`` and root."""
    paths = sorted((root / "experiments").glob("*.duckdb"))
    root_store = root / "experiment.duckdb"
    if root_store.exists():
        paths.append(root_store)
    return tuple(paths)


@dataclass(frozen=True, slots=True)
class GeometryCoverage:
    """One geometry's PASS cells, split by whether the credit reads error."""

    error_aware: tuple[str, ...]
    error_aware_cells: Mapping[str, int]
    error_blind: tuple[str, ...]
    pass_cells: int


@dataclass(frozen=True, slots=True)
class CorpusCoverage:
    """The corpus counted once: axes, geometries, tasks, and unreadable stores."""

    stores: tuple[str, ...]
    unreadable: Mapping[str, str]
    pass_cells: int
    axes: Mapping[str, tuple[tuple[str, ...], tuple[str, ...]]]
    geometries: Mapping[str, GeometryCoverage]
    tasks: Mapping[str, int]
    untouched_tasks: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "source": list(self.stores),
            "pass_cells": self.pass_cells,
            "axes": {
                axis: {"measured": list(measured), "missing": list(missing)}
                for axis, (measured, missing) in self.axes.items()
            },
            "geometries": {
                geometry: {
                    "error_aware": list(row.error_aware),
                    "error_aware_cells": dict(row.error_aware_cells),
                    "error_blind": list(row.error_blind),
                    "n_error_aware": len(row.error_aware),
                    "pass_cells": row.pass_cells,
                }
                for geometry, row in self.geometries.items()
            },
            "tasks": dict(self.tasks),
            "untouched_tasks": list(self.untouched_tasks),
            "unreadable": dict(self.unreadable),
        }

    def render(self) -> str:
        """The report a reader receives; the probe's numbers, as text."""
        lines = [
            f"Corpus coverage: {self.pass_cells} PASS cells over "
            f"{len(self.stores)} readable store(s)",
            "=" * 80,
            "",
            "Per-Axis Coverage (measured / declared):",
        ]
        for axis, (measured, missing) in self.axes.items():
            declared = len(measured) + len(missing)
            pct = 100.0 * len(measured) / max(1, declared)
            lines.append(f"  {axis}: {len(measured)} / {declared} ({pct:.1f}%)")
            lines.append(f"    Measured: {list(measured)}")
            if missing:
                lines.append(f"    Missing: {list(missing)}")

        lines.extend(["", "Per-Geometry Error-Aware Credits:"])
        for geometry, row in self.geometries.items():
            cells = ", ".join(
                f"{credit}={count}"
                for credit, count in sorted(row.error_aware_cells.items())
            )
            lines.append(
                f"  {geometry}: {len(row.error_aware)} error-aware "
                f"({cells or 'none'}); pass={row.pass_cells}"
            )
            if row.error_blind:
                lines.append(f"    error-blind (excluded): {list(row.error_blind)}")

        lines.extend(["", "Per-Task Coverage:"])
        for task, cells in self.tasks.items():
            lines.append(f"  {task}: {cells} PASS cells")
        if self.untouched_tasks:
            lines.append(f"  NOT TOUCHED: {list(self.untouched_tasks)}")
        else:
            lines.append("  every registered task is measured")

        if self.unreadable:
            lines.extend(["", "Unreadable stores (reported, never skipped):"])
            for path, reason in self.unreadable.items():
                lines.append(f"  {path}: {reason}")
        return "\n".join(lines)


def _axis_coverage(
    seen: Mapping[str, set[str]],
) -> dict[str, tuple[tuple[str, ...], tuple[str, ...]]]:
    coverage: dict[str, tuple[tuple[str, ...], tuple[str, ...]]] = {}
    for axis_name, names in seen.items():
        axis_enum = StructuralAxis[axis_name.upper()]
        declared = set(AXES_REGISTRIES[axis_enum].keys())
        coverage[axis_name] = (tuple(sorted(names)), tuple(sorted(declared - names)))
    return coverage


def scan_corpus(paths: Iterable[Path], *, root: Path | None = None) -> CorpusCoverage:
    """Count every readable store once: PASS records per axis, geometry and task.

    Args:
        paths: Store files to read.
        root: Directory that store paths are reported relative to.

    Returns:
        The corpus coverage. A store that cannot be read is named in
        ``unreadable`` with its error, never dropped silently.
    """
    seed_all_registries()
    from computronium.experiment.registry.task_registry import TaskRegistry

    geometries = tuple(sorted(AXES_REGISTRIES[StructuralAxis.GEOMETRY].keys()))
    seen_axes: dict[str, set[str]] = {axis.value: set() for axis in StructuralAxis}
    covered: dict[str, dict[str, int]] = {geometry: {} for geometry in geometries}
    tasks: dict[str, int] = {}
    unreadable: dict[str, str] = {}
    readable: list[str] = []
    pass_cells = 0

    for path in paths:
        label = str(path.relative_to(root)) if root else str(path)
        try:
            with RecordStore(StoreConfig(path=path, read_only=True)) as store:
                records = store.query_records()
        except Exception as error:  # ruff: ignore[blind-except] - a stale store is data
            unreadable[label] = str(error)
            continue
        readable.append(label)
        for record in records:
            if record.status.gate_verdict.value != "PASS":
                continue
            pass_cells += 1
            for axis in seen_axes:
                seen_axes[axis].add(getattr(record, axis))
            if record.geometry in covered:
                covered[record.geometry][record.credit] = (
                    covered[record.geometry].get(record.credit, 0) + 1
                )
            tasks[record.schedule.task_id] = tasks.get(record.schedule.task_id, 0) + 1

    geometry_rows: dict[str, GeometryCoverage] = {}
    for geometry, credits in covered.items():
        error_aware = {
            credit: count
            for credit, count in credits.items()
            if not error_blind_credit(credit)
        }
        error_blind = {
            credit: count
            for credit, count in credits.items()
            if error_blind_credit(credit)
        }
        geometry_rows[geometry] = GeometryCoverage(
            error_aware=tuple(sorted(error_aware)),
            error_aware_cells=error_aware,
            error_blind=tuple(sorted(error_blind)),
            pass_cells=sum(credits.values()),
        )

    registry_tasks = set(TaskRegistry()._enrichments.keys())
    return CorpusCoverage(
        stores=tuple(readable),
        unreadable=unreadable,
        pass_cells=pass_cells,
        axes=_axis_coverage(seen_axes),
        geometries=geometry_rows,
        tasks=dict(sorted(tasks.items())),
        untouched_tasks=tuple(sorted(registry_tasks - set(tasks))),
    )
