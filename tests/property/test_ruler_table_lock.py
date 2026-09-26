"""§3.2: no learning rate may depend on a file that is not in the repository.

`campaign._ruler_lr` read `artifacts/ruler_table.json` — a path inside a
gitignored directory, reached through a hardcoded `parents[2]` that does not
exist in an installed wheel. Its own docstring called it "the committed ruler
table". The table *is* re-derivable (`scripts/probes/ruler_calibration.py`
writes it), but nothing required anyone to have run it, and the `except` branch
degraded to a flat `1e-2` with a log line.

That fallback is not a cosmetic default. Measured over the table's 11 tasks,
**4 calibrate to `1e-3`** (xor, iris, wine, and one more), so a fresh clone
trained every one of them at 10x its calibrated learning rate, silently, and a
`logger.warning` is not a gate.

The table now ships inside the package and is read from `__file__`. These tests
are the reason that holds:

* the file the code reads is **tracked by git** — the invariant that was
  silently false before, and the one a rename or a `.gitignore` edit would
  break again;
* every task's resolved lr equals the table's own value, so the shipped data
  and the behaviour cannot drift apart;
* the table resolves *inside* the package, so an installed wheel has it.

Re-probing is a deliberate promotion, exactly like re-pinning a manifest: the
probe still writes to `artifacts/`, and moving a fresh run into the package is
an act someone has to perform and this lock will notice when they forget to
re-run the tests.
"""

from __future__ import annotations

import fnmatch
import json
import subprocess
import tomllib
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from computronium.autoscientist import campaign

if TYPE_CHECKING:
    from collections.abc import Iterator

REPO_ROOT = Path(__file__).resolve().parents[2]
TABLE = campaign._ruler_table_path()


@pytest.fixture(autouse=True)
def _clear_ruler_cache() -> Iterator[None]:
    """`_RULER_LR` is a module-level cache; a test must not inherit its state."""
    campaign._RULER_LR.clear()
    yield
    campaign._RULER_LR.clear()


type Row = dict[str, float | str | bool]


def _rows() -> list[Row]:
    rows: list[Row] = json.loads(TABLE.read_text(encoding="utf-8"))["rows"]
    return rows


def test_ruler_table_ships_inside_the_package() -> None:
    assert campaign._ruler_table_path() == TABLE, (
        "the lock must read the path the code opens, not one it reconstructs"
    )
    assert TABLE.is_file(), f"packaged ruler table missing at {TABLE}"
    assert TABLE.parent == Path(campaign.__file__).parent, (
        "the table must resolve next to campaign.py, or an installed wheel "
        "loses it and every task falls back to 1e-2"
    )


def test_ruler_table_is_tracked_by_git() -> None:
    """The invariant that was silently false: a gitignored table is no table."""
    tracked = subprocess.run(
        ["git", "ls-files", "--error-unmatch", str(TABLE.relative_to(REPO_ROOT))],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert tracked.returncode == 0, (
        f"{TABLE.relative_to(REPO_ROOT)} is not tracked; _ruler_lr will fall "
        "back to a flat 1e-2 on any clone, which is 10x the calibrated lr for "
        "the tasks that measure 1e-3"
    )


def test_wheel_would_carry_the_table() -> None:
    """`include-package-data` alone dropped it: measured, every .json was gone.

    With no MANIFEST.in and no VCS plugin, setuptools has nothing to resolve
    package data from, so the table was absent from a built wheel while the
    source tree looked fine -- the same class of claim as the gitignored path,
    one level down. Building a wheel per test run is not affordable, so this
    asserts the declaration that governs it.
    """
    config = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))[
        "tool"
    ]["setuptools"]
    patterns = config.get("package-data", {}).get("computronium", [])
    rel = TABLE.relative_to(REPO_ROOT / "computronium").as_posix()
    assert any(fnmatch.fnmatch(rel, pat) for pat in patterns), (
        f"no package-data pattern matches {rel}; patterns={patterns}. "
        "A wheel built from this tree would not carry the ruler table."
    )


def test_the_table_is_not_empty_and_covers_its_own_fallback() -> None:
    rows = _rows()
    assert len(rows) >= 10, "ruler table lost rows; every task now shares one lr"
    for row in rows:
        assert isinstance(row["lr"], int | float), f"{row['task']} has no lr"


@pytest.mark.parametrize("row", _rows(), ids=lambda r: str(r["task"]))
def test_resolved_lr_matches_the_shipped_table(row: Row) -> None:
    assert campaign._ruler_lr(str(row["task"])) == float(row["lr"])


def test_unknown_task_falls_back_to_the_star_default() -> None:
    assert campaign._ruler_lr("no_such_task") == campaign._ruler_lr(None) == 1e-2


def test_non_feedforward_topology_keeps_its_own_calibration() -> None:
    """The `1e-2` for other topologies is a *measured* probe result, not a default."""
    assert campaign._ruler_lr("digits", "recurrent") == 1e-2
    assert campaign._ruler_lr("digits", "feedforward") == 0.01
