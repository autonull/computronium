"""Print the SEC coverage map from a results root's per-primitive parts.

Usage: ``uv run python scripts/analysis/sec_map.py results/sec/serial3``

One row per primitive: its ladder verdict, the best point, and the named reason
of the first rung. The map is the artifact — viable, below_bar, error_blind,
all_refused, no_knob and skipped are distinct states, never one "failure" count.
"""

from __future__ import annotations

import collections
import json
import sys
from pathlib import Path

VERDICTS = ("viable", "below_bar", "error_blind", "all_refused", "no_cell")


def _rows(
    root: Path,
) -> tuple[list[tuple[str, str, str, str]], dict[str, collections.Counter]]:
    rows: list[tuple[str, str, str, str]] = []
    counts: dict[str, collections.Counter] = {}
    for axis_dir in sorted(p for p in root.iterdir() if p.is_dir()):
        counter: collections.Counter = collections.Counter()
        for path in sorted((axis_dir / "parts").glob("*.json")):
            part = json.loads(path.read_text(encoding="utf-8"))
            primitive = part["primitive"]
            if part["status"] == "skipped":
                counter["skipped"] += 1
                rows.append((axis_dir.name, primitive, "skipped", ""))
                continue
            if part["status"] == "error":
                counter["error"] += 1
                rows.append((
                    axis_dir.name,
                    primitive,
                    "error",
                    part["payload"].get("error", ""),
                ))
                continue
            payload: dict = part["payload"]
            verdict = str(payload.get("rung1_verdict"))
            counter[verdict] += 1
            best = payload.get("best_rung") or {}
            point = (
                f"{best.get('factor'):.3g}x = {best.get('val_acc'):.4f}"
                if best.get("factor") is not None and best.get("val_acc") is not None
                else ""
            )
            rungs = payload.get("rung1_ladder") or []
            reason = next(
                (str(r.get("reason") or "") for r in rungs if r.get("reason")), ""
            )
            rows.append((axis_dir.name, primitive, str(verdict), point or reason[:80]))
        counts[axis_dir.name] = counter
    return rows, counts


def main(argv: list[str]) -> int:
    root = Path(argv[1]) if len(argv) > 1 else Path("results/sec/serial3")
    if not root.exists():
        print(f"no results at {root}")
        return 2
    rows, counts = _rows(root)
    current = None
    for axis, primitive, verdict, detail in rows:
        if axis != current:
            current = axis
            print(f"\n## {axis}")
        print(f"  {primitive:24s} {verdict:12s} {detail}")
    print("\n## summary")
    for axis, counter in counts.items():
        viable = counter.get("viable", 0) + counter.get("error_blind", 0)
        total = sum(counter.values())
        print(
            f"  {axis:11s} viable+blind={viable:2d}/{total:2d}  {dict(sorted(counter.items()))}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
