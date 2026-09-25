#!/usr/bin/env python
"""Manual screenshot generation (GAME.todo7 §5.1) — dev tool, not a CI gate.

Captures the current UI as a glance-verification baseline before refactors::

    uv run python scripts/generate_dashboard_screenshots.py
    uv run python scripts/generate_dashboard_screenshots.py --serve --root artifacts/broad_map

No pixel diffs, no pass/fail. Screenshots land in ``tests/ui/screenshots/``
(gitignored via ``screenshots/``). Open the directory and eyeball it;
discard when the UI changes.
"""

from __future__ import annotations

import argparse
import subprocess  # ruff: ignore[suspicious-subprocess-import]
import sys
from pathlib import Path

OUT_DIR = Path("tests/ui/screenshots")
CAPTURE_TEST = "tests/ui/test_dashboard_screenshots.py"


def _capture() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", CAPTURE_TEST, "--capture-screenshots", "-q"],
        check=False,
    )
    if proc.returncode != 0:
        print("capture suite failed — see output above", flush=True)
        return proc.returncode
    shots = sorted(OUT_DIR.glob("*.png"))
    print(f"{len(shots)} screenshots in {OUT_DIR}/")
    for shot in shots:
        print(f"  {shot.name}")
    return 0


def _serve(root: str, port: int) -> int:
    proc = subprocess.run(
        ["uv", "run", "comp", "dashboard", "--root", root, "--port", str(port)],
        check=False,
    )
    return proc.returncode


def main() -> int:
    parser = argparse.ArgumentParser(prog="generate_dashboard_screenshots")
    parser.add_argument(
        "--serve",
        action="store_true",
        help="launch a live dashboard for eyeballing instead of capturing",
    )
    parser.add_argument("--root", default="artifacts/broad_map")
    parser.add_argument("--port", type=int, default=8088)
    args = parser.parse_args()
    if args.serve:
        return _serve(args.root, args.port)
    return _capture()


if __name__ == "__main__":
    raise SystemExit(main())
