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

    from computronium.experiment.legality.engine import VoidRule

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
    """The corpus counted once: axes, geometries, pairs, tasks, and unreadable stores."""

    stores: tuple[str, ...]
    unreadable: Mapping[str, str]
    pass_cells: int
    axes: Mapping[str, tuple[tuple[str, ...], tuple[str, ...]]]
    geometries: Mapping[str, GeometryCoverage]
    pairs: Mapping[tuple[str, str], int]
    pair_gaps: Mapping[tuple[str, str], tuple[tuple[str, str], ...]]
    pair_holes: tuple[tuple[str, str], ...]
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
            "pairs": {_pair_key(pair): cells for pair, cells in self.pairs.items()},
            "pair_gaps": {
                _pair_key(pair): "; ".join(f"{name}: {text}" for name, text in reason)
                for pair, reason in self.pair_gaps.items()
            },
            "pair_holes": [_pair_key(pair) for pair in self.pair_holes],
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

        declared_pairs = len(set(self.pairs) | set(self.pair_gaps))
        coupled = len([pair for pair in self.pairs if pair not in self.pair_gaps])
        lines.extend([
            "",
            "Substrate x Geometry Pairs:",
            f"  {len(self.pairs)} / {declared_pairs} hold a PASS cell "
            f"({coupled} on a coordinate no rule refuses)",
        ])
        lines.extend(_render_pairs(self.pairs, self.pair_gaps, self.pair_holes))

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


def _pair_key(pair: tuple[str, str]) -> str:
    return f"{pair[0]}/{pair[1]}"


def _declared(axis: StructuralAxis) -> tuple[str, ...]:
    return tuple(AXES_REGISTRIES[axis].keys())


#: The four axes a pair verdict is free to vary, outermost first.
_PAIR_FREE_AXES = (
    StructuralAxis.DYNAMICS,
    StructuralAxis.PLASTICITY,
    StructuralAxis.CREDIT,
    StructuralAxis.UPDATE,
)


def _refusal(
    selection: Mapping[str, str], rules: tuple[VoidRule, ...]
) -> tuple[VoidRule, frozenset[str]] | None:
    """The first rule that refuses this coordinate, with the names it reads."""
    from computronium.experiment.legality.dsl import (
        CoordinateContext,
        evaluate,
        referenced_names,
    )
    from computronium.experiment.schema.coordinate import Coordinate

    ctx = CoordinateContext(Coordinate(**selection, params={}), task=None)
    for rule in rules:
        if not evaluate(rule.predicate, ctx):
            return rule, referenced_names(rule.predicate)
    return None


def _void_witness(
    pair: tuple[str, str], rules: tuple[VoidRule, ...]
) -> tuple[tuple[str, str], ...]:
    """The rules that refuse every declared combination of a pair.

    A pair is void only when no values of the four remaining axes make it
    legal, so the search is exhaustive over them. It prunes on the refusal's
    own footprint: a rule that reads no credit refuses every credit, so the
    remaining credit values cannot overturn it. Every refusal the search meets
    is kept, because a void usually takes two rules — nca requires
    instantaneous dynamics and the neuromorphic substrate refuses it — and
    naming one of them alone hides the contradiction. The answer is then
    narrowed to the shallowest axis whose rules account for the refusal, so a
    credit-level rule does not enter the explanation of a dynamics-level
    contradiction. The verdict is read from the system's void rules, so
    deleting a rule turns its pairs back into holes. Because a pair verdict is
    task-free, a task-dependent rule is left out of the answer: a pair that
    some task can measure is reachable.
    """
    selection = {"substrate": pair[0], "geometry": pair[1]}
    met: dict[str, tuple[str, frozenset[str]]] = {}

    def search(
        axes: tuple[StructuralAxis, ...],
    ) -> tuple[VoidRule, frozenset[str]] | None:
        if not axes:
            refusal = _refusal(selection, rules)
            if refusal is not None:
                met.setdefault(refusal[0].name, (refusal[0].description, refusal[1]))
            return refusal
        axis, rest = axes[0], axes[1:]
        refusal = None
        for value in _declared(axis):
            selection[axis.value] = value
            refusal = search(rest)
            if refusal is None:
                return None
            if axis.value not in refusal[1]:
                return refusal
        return refusal

    if search(_PAIR_FREE_AXES) is None:
        return ()
    fixed = {"substrate", "geometry"}
    for axis in _PAIR_FREE_AXES:
        fixed.add(axis.value)
        shallow = {name: text for name, (text, names) in met.items() if names <= fixed}
        if shallow:
            return tuple(sorted(shallow.items()))
    return tuple(sorted((name, text) for name, (text, _) in met.items()))


def _pair_gaps(
    measured: Mapping[tuple[str, str], int],
) -> tuple[
    dict[tuple[str, str], tuple[tuple[str, str], ...]], tuple[tuple[str, str], ...]
]:
    """Classify every declared pair: refused by a rule, or an undeclared hole.

    A pair is judged by the system's void rules whether or not it holds cells:
    a cell on a coordinate a rule refuses cannot count toward breadth, and
    must not hide the refusal. A pair with no cells and no refusal is a hole —
    the defect the breadth rule names.
    """
    from computronium.experiment.legality.engine import void_rules

    rules = tuple(void_rules())
    gaps: dict[tuple[str, str], tuple[tuple[str, str], ...]] = {}
    holes: list[tuple[str, str]] = []
    for substrate in _declared(StructuralAxis.SUBSTRATE):
        for geometry in _declared(StructuralAxis.GEOMETRY):
            pair = (substrate, geometry)
            witness = _void_witness(pair, rules)
            if witness:
                gaps[pair] = witness
            elif pair not in measured:
                holes.append(pair)
    return gaps, tuple(holes)


def _render_pairs(
    pairs: Mapping[tuple[str, str], int],
    gaps: Mapping[tuple[str, str], tuple[tuple[str, str], ...]],
    holes: tuple[tuple[str, str], ...],
) -> list[str]:
    """The pair section: refused coordinates, cells that cannot count, holes."""
    lines = []
    if gaps:
        lines.append(f"  {len(gaps)} refused by a rule:")
        lines.extend(
            f"    {substrate} x {geometry}: {', '.join(name for name, _ in reason)}"
            for (substrate, geometry), reason in sorted(gaps.items())
        )
        legend = {name: text for reason in gaps.values() for name, text in reason}
        lines.extend(f"    {name}: {text}" for name, text in sorted(legend.items()))
        on_void = sorted(pair for pair in pairs if pair in gaps)
        if on_void:
            cells = sum(pairs[pair] for pair in on_void)
            lines.append(
                f"  {len(on_void)} of them hold a PASS cell ({cells} cells) that "
                "cannot count as substrate breadth:"
            )
            lines.extend(
                f"    {substrate} x {geometry} ({pairs[substrate, geometry]})"
                for substrate, geometry in on_void
            )
    if holes:
        lines.append("  UNMEASURED (no cell, no void row):")
        lines.extend(f"    {substrate} x {geometry}" for substrate, geometry in holes)
    else:
        lines.append("  no undeclared pair: every pair holds a cell or names a rule")
    return lines


def _geometry_rows(
    covered: Mapping[str, Mapping[str, int]],
) -> dict[str, GeometryCoverage]:
    """Split each geometry's PASS cells by whether the credit reads error."""
    rows: dict[str, GeometryCoverage] = {}
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
        rows[geometry] = GeometryCoverage(
            error_aware=tuple(sorted(error_aware)),
            error_aware_cells=error_aware,
            error_blind=tuple(sorted(error_blind)),
            pass_cells=sum(credits.values()),
        )
    return rows


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

    seen_axes: dict[str, set[str]] = {axis.value: set() for axis in StructuralAxis}
    covered: dict[str, dict[str, int]] = {
        geometry: {} for geometry in _declared(StructuralAxis.GEOMETRY)
    }
    pair_cells: dict[tuple[str, str], int] = {}
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
            pair = (record.substrate, record.geometry)
            pair_cells[pair] = pair_cells.get(pair, 0) + 1
            tasks[record.schedule.task_id] = tasks.get(record.schedule.task_id, 0) + 1

    registry_tasks = set(TaskRegistry()._enrichments.keys())
    pair_gaps, pair_holes = _pair_gaps(pair_cells)
    return CorpusCoverage(
        stores=tuple(readable),
        unreadable=unreadable,
        pass_cells=pass_cells,
        axes=_axis_coverage(seen_axes),
        geometries=_geometry_rows(covered),
        pairs=dict(sorted(pair_cells.items())),
        pair_gaps=pair_gaps,
        pair_holes=pair_holes,
        tasks=dict(sorted(tasks.items())),
        untouched_tasks=tuple(sorted(registry_tasks - set(tasks))),
    )
