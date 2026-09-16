"""``comp dashboard`` — the live window over a continuous-discovery root.

Read-only: polls the campaign artifacts (KB, voids, defects, burst log) and
re-renders on change only. No execution, no ledger writes.

Usage::

    uv run comp dashboard --root artifacts/broad_map --port 8088
    uv run comp dashboard --root artifacts/broad_map --log-path logs/continuous_500.log
"""

from __future__ import annotations

import argparse
from pathlib import Path

POLL_SECONDS = 2.0


def main() -> int:
    parser = argparse.ArgumentParser(prog="comp dashboard", description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("artifacts/broad_map"))
    parser.add_argument("--port", type=int, default=8088)
    parser.add_argument(
        "--log-path",
        type=Path,
        default=None,
        help="ticker source (default: newest logs/continuous*.log under --root)",
    )
    parser.add_argument(
        "--poll",
        type=float,
        default=POLL_SECONDS,
        help="artifact polling interval in seconds",
    )
    args = parser.parse_args()

    from nicegui import ui

    from computronium.visualization.live_atlas import build_dashboard

    build_dashboard(args.root, args.log_path, args.poll)
    ui.run(
        title="Computronium — Live Broad Map",
        port=args.port,
        reload=False,
        show=False,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
