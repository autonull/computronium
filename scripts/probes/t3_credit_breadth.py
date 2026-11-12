"""T3: is "≥3 error-aware credits per geometry" backed by a table?

The success criterion had no table behind it. This probe reads the existing
stores first (``experiments/*.duckdb`` plus the root store) and counts, per
declared geometry, the distinct credits with at least one PASS cell. Credits
that declare ``error_blind=True`` are excluded: they read no label, so on a
supervised task they measure chance by contract and never count.

A geometry with fewer than three error-aware credits is a named gap, not a
reason to run a sweep. Only a gap that the existing stores cannot fill is a
sweep candidate.

Run: uv run python scripts/probes/t3_credit_breadth.py
Measured (2026-11-12): 8 of 12 declared geometries reach three error-aware
credits from the stores alone (feedforward 8, recurrent 5, tile_mesh 5, conv 3,
causal_transformer 3, ntm 3, tile 4, attention 2, spatial_lattice 2, graph 2,
nca 1). The two-credit gaps are closed by ``t3_credit_gap_sweep.py`` for
attention and spatial_lattice (gradient works); nca and graph remain named
gaps. Thirty stores answer with a newer DuckDB storage version and are listed
under ``unreadable`` rather than silently skipped.
"""

from __future__ import annotations

import json
from pathlib import Path

from computronium.core.system_trainer.spec import _credit_from_config
from computronium.experiment.evidence.store import RecordStore, StoreConfig
from computronium.experiment.schema import AXES_REGISTRIES
from computronium.experiment.schema.axis import StructuralAxis
from computronium.experiment.schema.seed_registries import seed_all_registries
from computronium.ontology.credit import CreditAssignmentConfig

__all__ = ["main"]

ROOT = Path(__file__).resolve().parents[2]
RESULTS: dict[str, object] = {}


def _error_blind(credit: str) -> bool:
    factory = getattr(CreditAssignmentConfig, credit, None)
    if factory is None:
        return False
    return bool(_credit_from_config(factory()).error_blind)


def _stores() -> list[Path]:
    paths = sorted((ROOT / "experiments").glob("*.duckdb"))
    root = ROOT / "experiment.duckdb"
    if root.exists():
        paths.append(root)
    return paths


def main() -> int:
    seed_all_registries()
    geometries = tuple(sorted(AXES_REGISTRIES[StructuralAxis.GEOMETRY].keys()))
    covered: dict[str, dict[str, int]] = {geometry: {} for geometry in geometries}
    unreadable: dict[str, str] = {}

    for path in _stores():
        try:
            with RecordStore(StoreConfig(path=path, read_only=True)) as store:
                records = store.query_records()
        except Exception as error:  # ruff: ignore[blind-except] — a stale store is data, not a crash
            unreadable[str(path.relative_to(ROOT))] = str(error)
            continue
        for record in records:
            if record.status.gate_verdict.value != "PASS":
                continue
            if record.geometry not in covered:
                continue
            covered[record.geometry][record.credit] = (
                covered[record.geometry].get(record.credit, 0) + 1
            )

    table: dict[str, dict[str, object]] = {}
    missing: dict[str, list[str]] = {}
    for geometry, credits in covered.items():
        error_aware = {
            credit: count
            for credit, count in credits.items()
            if not _error_blind(credit)
        }
        error_blind = {
            credit: count for credit, count in credits.items() if _error_blind(credit)
        }
        table[geometry] = {
            "error_aware": sorted(error_aware),
            "error_aware_cells": error_aware,
            "error_blind": sorted(error_blind),
            "n_error_aware": len(error_aware),
            "pass_cells": sum(credits.values()),
        }
        if len(error_aware) < 3:
            missing[geometry] = sorted(error_aware)

    RESULTS["source"] = [str(path.relative_to(ROOT)) for path in _stores()]
    RESULTS["geometries"] = table
    RESULTS["missing"] = missing
    RESULTS["unreadable"] = unreadable
    print(json.dumps(RESULTS, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
