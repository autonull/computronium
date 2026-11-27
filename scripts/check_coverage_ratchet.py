"""A ratchet on the release population's line coverage (TODO108 W62).

The number is a direction, not a target: covered statements may not fall, and
a rise above the baseline by more than the slack is a **stale baseline** — the
change that covered more raises it in the same commit, so the next drop is
caught. A drop is reported with the files that lost the most lines, because
"coverage fell" without the file is not actionable.

Coverage is measured by ``COVERAGE=1 scripts/run_local_gates.sh``, which is the
population this ratchet is defined over: the release's own test selection.
"""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

BASELINE = Path("configs/coverage_ratchet.json")


def _summary(path: Path) -> tuple[int, int, dict[str, int]]:
    """(statements, covered, per-file missing) from a coverage JSON report."""
    payload = json.loads(path.read_text(encoding="utf-8"))
    totals = payload["totals"]
    missing = {
        name.split("computronium/")[-1]: info["summary"]["missing_lines"]
        for name, info in payload["files"].items()
    }
    return (
        int(totals["num_statements"]),
        int(totals["covered_lines"]),
        missing,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--coverage-json", type=Path, required=True)
    parser.add_argument("--update", action="store_true")
    args = parser.parse_args()

    statements, covered, missing = _summary(args.coverage_json)
    baseline = json.loads(BASELINE.read_text(encoding="utf-8"))
    measured = {
        "population": baseline["population"],
        "statements": statements,
        "covered": covered,
        "percent": round(100 * covered / max(statements, 1), 2),
        "slack": baseline["slack"],
        "measured": date.today().isoformat(),
    }
    if args.update:
        BASELINE.write_text(json.dumps(measured, indent=2) + "\n", encoding="utf-8")
        print(f"updated {BASELINE}: {measured}")
        return 0

    floor = baseline["covered"] - baseline["slack"]
    if covered < floor:
        worst = sorted(missing.items(), key=lambda item: -item[1])[:5]
        print(
            f"coverage fell: {covered} covered statements < floor {floor} "
            f"(baseline {baseline['covered']}, slack {baseline['slack']})",
        )
        for name, lost in worst:
            print(f"  {lost:5d} missing  {name}")
        return 1

    if covered > baseline["covered"] + baseline["slack"]:
        print(
            f"coverage rose to {covered} (baseline {baseline['covered']}); "
            "re-baseline with --update in this commit so the floor follows",
        )
        return 0

    print(
        f"coverage held: {covered} / {statements} statements "
        f"({100 * covered / max(statements, 1):.1f}%), floor {floor}",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
