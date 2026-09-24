"""``comp dashboard`` — the live window over a continuous-discovery root.

Read-only: polls the campaign artifacts (KB, voids, defects, burst log) and
re-renders on change only. No execution, no ledger writes.

Usage::

    uv run comp dashboard --root artifacts/broad_map --port 8088 [--ui-mode explorer|lab|auto] [--ui-actions on|off] [--quiet]
    uv run comp dashboard --root artifacts/broad_map,artifacts/other   # multi-root selector
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path

POLL_SECONDS = 2.0


def parse_roots(spec: str) -> tuple[Path, ...]:
    """Split a comma-separated ``--root`` spec into non-empty paths."""
    roots = tuple(Path(part.strip()) for part in spec.split(",") if part.strip())
    return roots or (Path("artifacts/broad_map"),)


def main() -> int:
    parser = argparse.ArgumentParser(prog="comp dashboard", description=__doc__)
    parser.add_argument(
        "--root",
        type=str,
        default="artifacts/broad_map",
        help="campaign root(s); comma-separated paths enable the header root selector",
    )
    parser.add_argument("--port", type=int, default=8088)
    parser.add_argument(
        "--log-path",
        type=Path,
        default=None,
        help="ticker source (default: newest continuous*.log in <root>/logs/ or logs/)",
    )
    parser.add_argument(
        "--poll",
        type=float,
        default=POLL_SECONDS,
        help="artifact polling interval in seconds",
    )
    parser.add_argument(
        "--daemon-url",
        type=str,
        default=None,
        help="lifecycle API base (e.g. http://127.0.0.1:8940). Adds the "
        "Start/Pause/Stop bar + live badge; without it the dashboard is "
        "artifact-polling only",
    )
    parser.add_argument(
        "--no-open",
        action="store_true",
        help="do not open a browser tab (headless/server use)",
    )
    parser.add_argument(
        "--ui-mode",
        choices=["explorer", "lab", "auto"],
        default=os.environ.get("COMPUTRONIUM_UI_MODE", "auto"),
        help="UI register: explorer (plain), lab (technical), auto (default)",
    )
    parser.add_argument(
        "--ui-actions",
        choices=["on", "off"],
        default=os.environ.get("COMPUTRONIUM_UI_ACTIONS", "off"),
        help="Enable UI actions (workshop, recipe editor)",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Compact text-only status chip; hides action lines, batches stream",
    )
    args = parser.parse_args()

    from nicegui import ui

    from computronium.ui.dashboard import build_dashboard

    roots = parse_roots(args.root)

    # An explicit page (not NiceGUI's auto-index) — script-mode
    # re-execution fails under a console-script entry point.
    @ui.page("/", language="en")  # type: ignore[arg-type]
    def _dashboard_page() -> None:
        build_dashboard(
            roots[0],
            args.log_path,
            args.poll,
            args.daemon_url,
            ui_mode=args.ui_mode,
            ui_actions=args.ui_actions == "on",
            quiet=args.quiet,
            roots=roots,
        )

    ui.run(
        title="Computronium — Live Broad Map",
        port=args.port,
        reload=False,
        show=not args.no_open,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
