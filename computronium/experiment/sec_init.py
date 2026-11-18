"""SEC Init: Initialize portfolio and cell log.

Run:
    uv run python -m computronium.experiment.sec_init --out results/sec
"""

from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Mapping


@dataclass(frozen=True, slots=True)
class TrackPortfolioEntry:
    """One track in the portfolio."""

    track: str
    rank: int
    kill_rule: str
    last_result: str  # claim, coordinate, defect, running, unstarted
    budget_used: dict[str, float]
    contention: bool


@dataclass(frozen=True, slots=True)
class PrimitiveMapEntry:
    """One primitive in the capability map."""

    primitive: str
    status: str  # known, unscreened, defect, unavailable, coordinate
    family: str
    box: dict
    ruler: str
    best_coordinate: dict | None
    defect: str | None
    capability: str
    last_screened: str | None


DEFAULT_TRACKS: list[TrackPortfolioEntry] = [
    TrackPortfolioEntry(
        track="R1",
        rank=1,
        kill_rule="worst-case gap < 2 pp on 5 seeds",
        last_result="unstarted",
        budget_used={"cells": 0, "seeds": 0, "forward_equivalents": 0.0},
        contention=False,
    ),
    TrackPortfolioEntry(
        track="R2",
        rank=2,
        kill_rule="worst-case gap < 2 pp on 5 seeds (20 tasks)",
        last_result="unstarted",
        budget_used={"cells": 0, "seeds": 0, "forward_equivalents": 0.0},
        contention=False,
    ),
    TrackPortfolioEntry(
        track="P0",
        rank=3,
        kill_rule=">20% DEFECT → pause R, fix",
        last_result="unstarted",
        budget_used={"cells": 0, "primitives": 0},
        contention=False,
    ),
    TrackPortfolioEntry(
        track="P1",
        rank=4,
        kill_rule="No effect → coordinate, not claim",
        last_result="unstarted",
        budget_used={"cells": 0, "seeds": 0},
        contention=False,
    ),
]


def write_portfolio(out_dir: Path) -> None:
    """Initialize portfolio.json."""
    out_dir.mkdir(parents=True, exist_ok=True)
    portfolio_path = out_dir / "portfolio.json"

    data = {
        "initialized_at": datetime.now().isoformat(),
        "version": "SEC-v2",
        "tracks": [asdict(t) for t in DEFAULT_TRACKS],
        "active_track": "R1",
        "session_count": 0,
    }

    portfolio_path.write_text(json.dumps(data, indent=2, default=str))
    print(f"Portfolio written to {portfolio_path}")


def write_cell_log(out_dir: Path) -> None:
    """Initialize empty cells.jsonl."""
    out_dir.mkdir(parents=True, exist_ok=True)
    cell_log_path = out_dir / "cells.jsonl"

    if not cell_log_path.exists():
        cell_log_path.write_text("")
        print(f"Cell log initialized at {cell_log_path}")
    else:
        print(f"Cell log already exists at {cell_log_path}")


def write_map(out_dir: Path) -> None:
    """Initialize empty map.json."""
    out_dir.mkdir(parents=True, exist_ok=True)
    map_path = out_dir / "map.json"

    if not map_path.exists():
        data = {
            "initialized_at": datetime.now().isoformat(),
            "version": "SEC-v2",
            "primitives": {},
        }
        map_path.write_text(json.dumps(data, indent=2))
        print(f"Map written to {map_path}")
    else:
        print(f"Map already exists at {map_path}")


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="SEC Init - initialize portfolio and cell log")
    parser.add_argument("--out", type=Path, required=True, help="Output directory")
    args = parser.parse_args()

    write_portfolio(args.out)
    write_cell_log(args.out)
    write_map(args.out)


if __name__ == "__main__":
    main()