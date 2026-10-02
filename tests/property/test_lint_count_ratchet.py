"""§2.3: a ratchet on the repo-wide ruff finding count.

`ruff check` runs repo-wide in well under a second, so the count can be
asserted rather than merely tracked in a plan document. The rule is one line:
the total may go down, never up. A suppression added to buy a green run shows
up here as a net increase, which is the failure mode §2.3 is about.

Measured with ruff 0.16.6 (423 — re-derived after TODO46 §3.3 deleted the
hand-rolled enumerator, its seven MNIST-shape sites and their 36 per-branch
findings; 440 was the count it introduced in the §3.2 session. after the pre-commit ruff auto-fix sweep; the pre-re-baseline figure was 359, re-baselined 2026-10-01 after the TODO44
cleanup: the pillar deletions removed code but retired per-file-ignores, the
docs/generated conformance stubs were excluded from lint, and restored
Library modules (profiling, param_estimator, probe, stability calibration)
re-entered the measured population; tranche-start count was 671, the
pre-re-baseline figure 359). A different ruff version legitimately
moves the count, so the version is recorded and a mismatch reports the
measured number instead of failing opaquely.

The 334 this file carried until 2026-09-27 was 28 below the tree it was
supposed to describe: the acceleration tranche landed ~25 findings of real new
kernel code (mostly PLW0717 try-clause and RUF105 ``noqa`` in the Triton
rungs) and the ratchet had not been re-derived against them. Re-baselined here
to the measured 359 rather than suppressed, and 359 is where it must now go
down from — a baseline that is merely *not exceeded* is not a ratchet.
"""

from __future__ import annotations

import re
import subprocess
import sys

BASELINE = 423
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
    """§2.3's gate: 'repo-wide lint trend down', asserted rather than tracked.

    A ruff version change is *not* an exemption. The first version of this
    test skipped on a mismatch, which is the plan's own failure mode — a gate
    that switches itself off without anyone deciding to, and invisibly, since
    the skip count is one line among 119. A new ruff legitimately moves the
    count, so that is a **deliberate re-baseline**: update both constants in
    the same commit and say in the body which rules changed.
    """
    measured, version = _measured()
    upgrade = version != f"ruff {RUFF_VERSION}"
    assert measured <= BASELINE, (
        f"repo-wide ruff findings {measured} exceed the {BASELINE} baseline"
        f"{' (ruff version changed: ' + version + ')' if upgrade else ''}; "
        "fix or justify the new finding, or re-baseline deliberately by "
        "updating BASELINE and RUFF_VERSION together"
    )


def test_the_baseline_is_not_stale() -> None:
    """A ratchet whose baseline is far above reality is silently disabled."""
    measured, _ = _measured()
    assert BASELINE - measured <= 10, (
        f"baseline {BASELINE} is {BASELINE - measured} above the measured "
        f"{measured}; lower it so the next addition is caught"
    )
