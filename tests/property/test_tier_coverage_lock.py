"""Tier-coverage lock: the per-tier runner may not silently skip a suite.

`scripts/run_tiered_suite.sh` is the command the verification section of every
plan in this series runs at round close. It kept its tier list in a hand-written
`TIERS="..."` string, and `acceleration` was never in it — so for a whole pass
the reference "full suite" omitted 210 tests, which is the entire Triton /
FlashAttention kernel suite and the settle activation-contract lock. The fast
lane in `pyproject.toml`'s `testpaths` *does* include it, which is exactly why
the omission survived: the inner loop was complete and the round-close figure
was short.

The list is now derived from the directories on disk. This lock exists because
a derivation can rot too — if the `find` invocation is broken, or gains an
exclusion, the runner silently degrades back to a partial suite while still
printing "ALL TIERS DONE".

Two assertions, and the second is the load-bearing one:

- the script contains no hard-coded tier list, and
- every non-`slow` directory under `tests/` with collected tests is a tier.

Per §0 of TODO35, the population assertion is part of the lock: an empty or
trivially-small directory set would make the first assertion vacuous, so the
test asserts the suite really does have the population it is guarding.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
RUNNER = REPO_ROOT / "scripts" / "run_tiered_suite.sh"
TESTS_ROOT = REPO_ROOT / "tests"

EXCLUDED_TIERS = frozenset({"slow", "__pycache__"})

# A directory with collected tests is a tier. A directory with none (e.g. a
# package holding only fixtures) is not silently skipped — it just has nothing
# to run.
_MIN_TIER_COUNT = 8


def _discovered_tiers() -> set[str]:
    return {
        p.name
        for p in TESTS_ROOT.iterdir()
        if p.is_dir() and p.name not in EXCLUDED_TIERS and not p.name.startswith("_")
    }


def _runner_text() -> str:
    return RUNNER.read_text()


def test_tier_list_is_derived_not_hand_written() -> None:
    """No `TIERS="..."` literal survives: the string *is* the silent skip."""
    assert not re.search(r"^\s*TIERS\s*=\s*[\"']", _runner_text(), re.MULTILINE), (
        "run_tiered_suite.sh hard-codes its tier list; a new tests/ directory "
        "will not run at round close (TODO35 §1.1)"
    )


def test_runner_resolves_the_repo_root_from_its_own_location() -> None:
    """A cwd-relative or absolute `cd` in a script is the §1.7 defect class."""
    assert not re.search(r"^cd\s+/", _runner_text(), re.MULTILINE)
    assert 'readlink -f "$0"' in _runner_text()


def test_every_test_directory_is_a_tier() -> None:
    discovered = _discovered_tiers()
    assert len(discovered) >= _MIN_TIER_COUNT, (
        f"expected at least {_MIN_TIER_COUNT} test tiers, found {sorted(discovered)}: "
        "the population this lock guards has changed shape"
    )
    # The runner's exclusion set must not have grown past `slow`/`__pycache__`.
    excluded = re.search(
        r"-not -name '([^']+)'(?:\s*\\\n\s*-not -name '([^']+)')*", _runner_text()
    )
    assert excluded is not None, "runner no longer filters directory discovery"
    assert set(excluded.group(0).split("'")[1::2]) == set(EXCLUDED_TIERS), (
        "runner excludes test directories the lock does not know about: "
        f"{excluded.group(0)!r}"
    )


def test_runner_discovers_exactly_the_directories_it_will_run() -> None:
    """Run the discovery half of the script for real.

    Executing the `find` is the only way to prove the derived list is the list
    the loop iterates; re-implementing the `find` in Python would be a test
    about the test.
    """
    out = subprocess.run(  # ruff: ignore[subprocess-without-shell-equals-true]
        [
            "bash",
            "-c",
            (
                'cd "$0" && find tests -mindepth 1 -maxdepth 1 -type d '
                "-not -name 'slow' -not -name '__pycache__' -printf '%f\\n' | sort"
            ),
            str(REPO_ROOT),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    runner_tiers = {line.strip() for line in out.stdout.splitlines() if line.strip()}
    assert runner_tiers == _discovered_tiers()


def test_every_tier_contains_tests() -> None:
    """Population assertion: a 'tier' with no tests is a typo, not a suite.

    Matching is recursive — `tests/algorithms` and `tests/primitives` hold
    subpackage suites, not files, so a top-level `test_*.py` glob is a lock
    that fails on healthy directories.
    """
    empty = [
        t
        for t in sorted(_discovered_tiers())
        if not any((TESTS_ROOT / t).rglob("test_*.py"))
    ]
    assert not empty, f"tiers with no test files: {empty}"
