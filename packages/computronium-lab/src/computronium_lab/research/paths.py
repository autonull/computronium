"""Stable corpus data/result paths (TODO24 T24.0.5, RESEARCH3 E-3 layout).

``data/research/todo24/`` holds persistent corpus inputs (frontier archive,
curricula); ``results/todo24/<problem_class>/<seed>/<timestamp>/`` holds one
``manifest.json`` per measurement run.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

__all__ = [
    "corpus_root",
    "results_dir",
    "write_manifest",
]

_CORPUS_ROOT = Path("data/research/todo24")
_RESULTS_ROOT = Path("results/todo24")


def corpus_root() -> Path:
    """Persistent corpus input directory (created on demand)."""
    _CORPUS_ROOT.mkdir(parents=True, exist_ok=True)
    return _CORPUS_ROOT


def results_dir(problem_class: str, seed: int, *, timestamp: str | None = None) -> Path:
    """Timestamped results directory for one (problem class, seed) run."""
    stamp = timestamp or datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    path = _RESULTS_ROOT / problem_class / str(seed) / stamp
    path.mkdir(parents=True, exist_ok=True)
    return path


def write_manifest(directory: Path, payload: object) -> Path:
    """Write ``manifest.json`` (sorted keys) and return its path."""
    manifest = directory / "manifest.json"
    manifest.write_text(
        json.dumps(payload, sort_keys=True, indent=2, default=str),
        encoding="utf-8",
    )
    return manifest
