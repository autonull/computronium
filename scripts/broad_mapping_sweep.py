"""Thin CLI wrapper over :mod:`computronium.autoscientist.broad_map` (TODO29 Phase 1).

The library lives in the package; this script only parses arguments.

Usage::

    nohup uv run python scripts/broad_mapping_sweep.py \
        --sample-size 500 --epochs 1 \
        --root artifacts/broad_map > logs/broad_map.log 2>&1 &
"""

from __future__ import annotations

import argparse
from pathlib import Path

from computronium.autoscientist.broad_map import main


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sample-size", type=int, default=500)
    parser.add_argument("--cells-per-iter", type=int, default=10)
    parser.add_argument("--epochs", type=int, default=1)
    parser.add_argument("--task", default="mnist")
    parser.add_argument("--seed", type=int, default=20260915)
    parser.add_argument("--max-iterations", type=int, default=200)
    parser.add_argument("--root", type=Path, default=Path("artifacts/broad_map"))
    parser.add_argument(
        "--hidden-dim", type=int, default=64, help="Geometry width for all cells"
    )
    parser.add_argument(
        "--depth", type=int, default=2, help="Geometry depth for all cells"
    )
    parser.add_argument(
        "--param-budget",
        type=int,
        default=25000,
        help="Geometry parameter budget per cell (0 = no rematch). One "
        "hidden_dim rescale per cell brings topologies within ~25%% of the "
        "budget — fixed depth/hidden spans a ~400x param spread.",
    )
    parser.add_argument(
        "--credit-trace",
        action="store_true",
        help="Capture per-cell BP-gradient alignment (credit_trace "
        "instrument: settle phases + split-half + BP reference on one "
        "batch). Adds settle overhead per cell.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    main(_parse_args())
