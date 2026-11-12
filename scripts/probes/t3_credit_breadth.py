"""T3: is "≥3 error-aware credits per geometry" backed by a table?

The success criterion had no table behind it. This probe reads the existing
stores first (``experiments/*.duckdb`` plus the root store) and counts, per
declared geometry, the distinct credits with at least one PASS cell. Credits
that declare ``error_blind=True`` are excluded: they read no label, so on a
supervised task they measure chance by contract and never count.

A geometry with fewer than three error-aware credits is a named gap, not a
reason to run a sweep. Only a gap that the existing stores cannot fill is a
sweep candidate.

The counting lives in ``computronium.experiment.evidence.corpus``: this probe
and ``comp coverage report --corpus`` read one implementation, and the lock in
``tests/property/test_corpus_coverage_lock.py`` compares their numbers.

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

import argparse
import json
from pathlib import Path

from computronium.experiment.evidence.corpus import (
    default_store_paths,
    scan_corpus,
)

__all__ = ["main"]

ROOT = Path(__file__).resolve().parents[2]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="Corpus root holding experiments/*.duckdb (default: repo root)",
    )
    args = parser.parse_args(argv)
    root = args.root.resolve()
    coverage = scan_corpus(default_store_paths(root), root=root)
    results = coverage.to_dict()
    results["missing"] = {
        geometry: list(row.error_aware)
        for geometry, row in coverage.geometries.items()
        if len(row.error_aware) < 3
    }
    print(json.dumps(results, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
