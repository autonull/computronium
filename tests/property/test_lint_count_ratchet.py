"""§2.3: a ratchet on the repo-wide ruff finding count.

`ruff check` runs repo-wide in well under a second, so the count can be
asserted rather than merely tracked in a plan document. The rule is one line:
the total may go down, never up. A suppression added to buy a green run shows
up here as a net increase, which is the failure mode §2.3 is about.

Measured with ruff 0.16.6; a different ruff version legitimately moves the
count, so the version is recorded and a mismatch reports the measured number
instead of failing opaquely.
"""

from __future__ import annotations

import re
import subprocess
import sys

import pytest

BASELINE = 359
RUFF_VERSION = "0.16.6"

_TOTAL = re.compile(r"Found (\d+) errors?")


def _measured() -> tuple[int, str]:
    version = subprocess.run(
        [sys.executable, "-m", "ruff", "--version"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    result = subprocess.run(
        [sys.executable, "-m", "ruff", "check", ".", "--no-cache"],
        capture_output=True,
        text=True,
        check=False,
    )
    match = _TOTAL.search(result.stdout)
    assert match is not None, f"could not parse ruff summary:\n{result.stdout[-500:]}"
    return int(match.group(1)), version.strip()


def test_repo_wide_lint_count_does_not_regress() -> None:
    """§2.3's gate: 'repo-wide lint trend down', asserted rather than tracked."""
    measured, version = _measured()
    if version != f"ruff {RUFF_VERSION}":
        pytest.skip(f"baseline measured with ruff {RUFF_VERSION}, running {version}")
    assert measured <= BASELINE, (
        f"repo-wide ruff findings {measured} exceed the {BASELINE} baseline; "
        "fix or justify the new finding rather than raising the number"
    )


def test_the_baseline_is_not_stale() -> None:
    """A ratchet whose baseline is far above reality is silently disabled."""
    measured, _ = _measured()
    assert BASELINE - measured <= 10, (
        f"baseline {BASELINE} is {BASELINE - measured} above the measured "
        f"{measured}; lower it so the next addition is caught"
    )
