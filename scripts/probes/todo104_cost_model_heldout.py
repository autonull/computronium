"""TODO104 7.2 probe: a box price predicts a held-out wave; a task price does not.

The wave pricer prices each cell from the positive control's measured epoch time
at the run's own box (``wave._first_wave_price``), falling back to a per-task
mean (``CostModel.cost_for``). This probe splits the measured SEC corpus by a
key, calibrates the per-cell price on the earlier half (median walltime) and
predicts the later half's total. Two keys are compared:

* ``task`` — the fallback table's key;
* ``task+geometry+dynamics+credit`` — the box the control measures.

Measured on ``results/sec/cells.jsonl`` (579 measured cells, 2026-11-25): the
box price predicts within the declared tolerance; the task-only price does not,
because one task's cells differ by two orders of magnitude (mnist feedforward
4.4 s vs a 130 s settle cell).
"""

from __future__ import annotations

import json
import statistics
import sys
from collections import defaultdict
from pathlib import Path

TOLERANCE = 0.5


def _cells(path: Path) -> list[tuple[dict[str, object], int, float]]:
    out = []
    for line in path.read_text(encoding="utf-8").splitlines(keepends=False):
        row = json.loads(line)
        screen = row.get("screen") or {}
        if screen.get("status") != "MEASURED":
            continue
        box = screen.get("box") or {}
        payload = (row.get("record") or {}).get("payload") or {}
        walltime = payload.get("walltime_s")
        if walltime:
            record = row.get("record") or {}
            out.append((box, record.get("seq", 0), float(walltime)))
    return out


def _errors(cells, key) -> list[float]:
    groups: dict[tuple, list[tuple[int, float]]] = defaultdict(list)
    for box, seq, walltime in cells:
        groups[key(box)].append((seq, walltime))
    errors = []
    for name, measured in sorted(groups.items(), key=lambda kv: -len(kv[1])):
        measured.sort()
        if len(measured) < 4:
            continue
        split = len(measured) // 2
        price = statistics.median(wall for _, wall in measured[:split])
        held_out = [wall for _, wall in measured[split:]]
        actual = sum(held_out)
        ratio = price * len(held_out) / actual if actual else float("inf")
        errors.append(abs(ratio - 1.0))
        print(
            f"  {name!s:60} calib={split:>3} held={len(held_out):>3} "
            f"price={price:7.2f}s ratio={ratio:5.2f}"
        )
    return errors


def main(path: Path = Path("results/sec/cells.jsonl")) -> int:
    cells = _cells(path)
    print(f"{len(cells)} measured cells from {path}")
    print("task key:")
    task_errors = _errors(cells, lambda box: box.get("task"))
    print("box key (task, geometry, dynamics, credit):")
    box_errors = _errors(
        cells,
        lambda box: (
            box.get("task"),
            box.get("geometry"),
            box.get("dynamics"),
            box.get("credit"),
        ),
    )
    for label, errors in (("task", task_errors), ("box", box_errors)):
        if errors:
            print(
                f"{label}: median |ratio-1| = {statistics.median(errors):.2f} "
                f"over {len(errors)} groups"
            )
    if not box_errors:
        print("FAIL: no box group had enough measured cells")
        return 1
    boxed = statistics.median(box_errors)
    print("PASS" if boxed <= TOLERANCE else "FAIL")
    return 0 if boxed <= TOLERANCE else 1


if __name__ == "__main__":
    raise SystemExit(main(*(Path(arg) for arg in sys.argv[1:])))
