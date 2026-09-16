"""Thin CLI wrapper over :mod:`computronium.visualization.atlas` (TODO29 Phase 1).

The library lives in the package; this script only parses arguments.

Usage::

    uv run python scripts/visualize_atlas.py --root artifacts/broad_map
"""

from __future__ import annotations

import argparse
from pathlib import Path

from computronium.visualization.atlas import main


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("artifacts/broad_map"))
    parser.add_argument("--task", default="mnist")
    parser.add_argument(
        "--ruler-table", type=Path, default=Path("artifacts/ruler_table.json")
    )
    parser.add_argument(
        "--png",
        type=Path,
        default=None,
        help="also render a static islands-&-voids PNG to this path",
    )
    parser.add_argument(
        "--multi-task",
        action="store_true",
        help="load all tasks and color islands by task (symbol by dynamics)",
    )
    return parser.parse_args()


if __name__ == "__main__":
    main(_parse_args())
