"""Ratchet on the repo-wide pyright error and warning counts.

TODO107 D4 makes lint and types ratchets rather than release blockers: the
count may go down, never up. ``ruff check`` has a test that asserts its count;
pyright is too slow for the per-commit hook, so its ratchet lives here and is
run by ``scripts/run_local_gates.sh``. ``--update`` rewrites the baseline after
a pass that lowered a count; a pass that only moves files is not a closure.
"""

from __future__ import annotations

import argparse
import json
import subprocess  # ruff: ignore[suspicious-subprocess-import] - pyright is the local tool
import sys
from datetime import date
from pathlib import Path

BASELINE = Path("configs/pyright_ratchet.json")


def _measured() -> dict[str, int | str]:
    result = subprocess.run(  # ruff: ignore[subprocess-without-shell-equals-true] - the command is fixed
        [  # ruff: ignore[start-process-with-partial-path] - pyright is on the venv PATH
            "pyright",
            "--outputjson",
            ".",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError:
        sys.stderr.write(result.stdout or result.stderr)
        msg = "pyright did not emit JSON"
        raise SystemExit(msg) from None
    summary = payload["summary"]
    return {
        "pyright_version": payload["version"],
        "errors": int(summary["errorCount"]),
        "warnings": int(summary["warningCount"]),
        "measured": date.today().isoformat(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--update",
        action="store_true",
        help="rewrite the baseline from the current tree (only after a lowering pass)",
    )
    args = parser.parse_args()

    measured = _measured()
    baseline = json.loads(BASELINE.read_text(encoding="utf-8"))
    if args.update:
        BASELINE.write_text(json.dumps(measured, indent=2) + "\n", encoding="utf-8")
        print(f"updated {BASELINE}: {measured}")
        return 0

    if measured["pyright_version"] != baseline["pyright_version"]:
        print(
            f"pyright {measured['pyright_version']} vs baseline "
            f"{baseline['pyright_version']}: a different engine may move the counts; "
            "re-baseline in the change that upgrades it."
        )

    errors_ok = measured["errors"] <= baseline["errors"]
    warnings_ok = measured["warnings"] <= baseline["warnings"]
    relation = (
        "lowered"
        if (
            measured["errors"] < baseline["errors"]
            or measured["warnings"] < baseline["warnings"]
        )
        else "held"
    )
    print(
        f"pyright ratchet {relation}: "
        f"{measured['errors']} errors ({baseline['errors']}), "
        f"{measured['warnings']} warnings ({baseline['warnings']})"
    )
    return 0 if errors_ok and warnings_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
