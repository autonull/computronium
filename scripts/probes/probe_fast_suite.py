"""Which test files buy the most line coverage per second (TODO108 W60).

Reads the coverage database of one full run (``--cov=computronium``
``--cov-context=test``) and the pytest ``--durations=0`` log, aggregates each
test file's executed lines and walltime, then greedily picks files by
``new lines / second`` until a target walltime. The output is the fast suite
and the files that buy the least, both measured rather than guessed.

Run::

    COVERAGE_FILE=/tmp/cov uv run python -m pytest <suites> \
        --cov=computronium --cov-context=test --durations=0 \
        --durations-min=0 > /tmp/durations.log
    uv run python scripts/probes/probe_fast_suite.py \
        --coverage-file /tmp/cov --durations-log /tmp/durations.log \
        --target-seconds 120

The context is a test node id with coverage.py's phase suffix
(``tests/...::test_x|run``); a context without ``::`` is the session's import
work, which any suite pays once, so it is reported beside the total rather
than charged to a file.
"""

from __future__ import annotations

import argparse
import re
import sqlite3
from collections import Counter, defaultdict
from pathlib import Path

from coverage.numbits import numbits_to_nums

_DURATION = re.compile(r"^(\d+(?:\.\d+)?)s\s+(?:setup|call|teardown)\s+(\S+)")
_PHASES = frozenset({"setup", "run", "teardown"})
type Line = tuple[str, int]


def _durations(log: Path) -> dict[str, float]:
    """Per test id, its summed walltime across phases."""
    totals: dict[str, float] = defaultdict(float)
    for line in log.read_text(encoding="utf-8", errors="replace").splitlines():
        match = _DURATION.match(line)
        if match is not None:
            totals[match.group(2)] += float(match.group(1))
    return dict(totals)


def _test_id(context: str) -> str:
    """The test id from coverage's ``<test id>|<phase>`` context.

    A parametrized id contains ``|`` itself (``[instantaneous|adam]``), so the
    phase is stripped from the end and only when it is a known phase.
    """
    head, sep, tail = context.rpartition("|")
    return head if sep and tail in _PHASES else context


def _covered_lines(path: Path) -> tuple[dict[str, set[Line]], set[Line]]:
    """(test id -> lines, import-only lines) from the coverage store."""
    con = sqlite3.connect(path)
    files = {row[0]: row[1] for row in con.execute("select id, path from file")}
    contexts = {
        row[0]: row[1] for row in con.execute("select id, context from context")
    }
    per_test: dict[str, set[Line]] = defaultdict(set)
    imports: set[Line] = set()
    for file_id, context_id, numbits in con.execute(
        "select file_id, context_id, numbits from line_bits"
    ):
        base = str(Path(files[file_id]))
        test_id = _test_id(contexts[context_id])
        target = per_test[test_id] if "::" in test_id else imports
        target.update((base, num) for num in numbits_to_nums(numbits))
    return per_test, imports


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--coverage-file", type=Path, required=True)
    parser.add_argument("--durations-log", type=Path, required=True)
    parser.add_argument("--target-seconds", type=float, default=120.0)
    parser.add_argument("--worst", type=int, default=12)
    args = parser.parse_args()

    durations = _durations(args.durations_log)
    per_test, imports = _covered_lines(args.coverage_file)

    by_file: dict[str, set[Line]] = defaultdict(set)
    seconds: dict[str, float] = defaultdict(float)
    for test_id, lines in per_test.items():
        source = test_id.split("::", 1)[0]
        by_file[source] |= lines
        seconds[source] += durations.get(test_id, 0.0)

    union: set[Line] = set().union(*by_file.values())
    occurrences: Counter[Line] = Counter()
    for lines in by_file.values():
        occurrences.update(lines)

    chosen: list[str] = []
    covered: set[Line] = set()
    spent = 0.0
    while spent < args.target_seconds:
        remaining = {f: by_file[f] - covered for f in by_file if f not in chosen}
        if not remaining:
            break
        best = max(
            remaining,
            key=lambda f: len(remaining[f]) / max(seconds[f], 1e-6),
        )
        if not remaining[best]:
            break
        chosen.append(best)
        covered |= by_file[best]
        spent += seconds[best]
        print(
            f"{spent:8.1f}s {100 * len(covered) / max(len(union), 1):5.1f}% "
            f"+{len(remaining[best]):6d}  {seconds[best]:7.1f}s  {best}"
        )

    print()
    print(
        f"traced per-test lines {len(union)}; import-only "
        f"{len(imports - union)}; statements are the denominator from "
        "`coverage report`"
    )
    print(
        f"fast suite: {len(chosen)} files, {spent:.1f}s, "
        f"{100 * len(covered) / max(len(union), 1):.1f}% of per-test lines"
    )

    unique = {
        f: sum(1 for line in by_file[f] if occurrences[line] == 1) for f in by_file
    }
    print(f"files with no unique line: {sum(1 for n in unique.values() if n == 0)}")
    worst = sorted(by_file, key=lambda f: len(by_file[f]) / max(seconds[f], 1e-6))[
        : args.worst
    ]
    print("lowest lines/second (lines, unique, seconds):")
    for source in worst:
        print(
            f"  {len(by_file[source]):6d} {unique[source]:5d} "
            f"{seconds[source]:8.1f}  {source}"
        )
    print("chosen files:")
    for source in chosen:
        print(f"  {source}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
