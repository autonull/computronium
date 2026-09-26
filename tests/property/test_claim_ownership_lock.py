"""A demo's claims are asserted by the demo that emits them (TODO35 §10.8-2).

F4 — the consolidated credit-channel failure map — used to hold eight
ratchets against the *committed records of five other demos*. It was a
cross-claim lock with no invalidation path: when D16's claim was inverted
at `2927ef33` and D14's numbers moved under a settle-horizon fix, F4 kept
asserting the retired claims and was red for every `slow` run for
nineteen days, behind a marker the default profile does not run. The
tests were fine; the claims they guarded had been retired by other
commits and nobody carried the guard with them.

Every one of those eight ratchets turned out to be a *duplicate* of a
claim its owning demo already asserts on its own fresh data — usually a
stronger one. So the fix was not to move claims around, it was to delete
the copies and make the owners' real claim functions runnable against
the committed record, which is what this file does.

Two locks, because the first is structural and the second is behavioural
and only one of them can see a claim that was never written:

* `test_no_test_reads_another_demos_record` — no test file may name a run
  record it does not emit. This is the defect class, expressed as a
  source scan, with the owner set as its population: a scan that finds
  nothing is the failure it is guarding against, so the population
  assertion is the *owner's* record reference existing at all.
* `test_owner_claims_hold_against_the_committed_record` — the owner's own
  `assert_claims` is *executed* against the committed record, in the fast
  lane, in seconds. A claim that stops holding stops the suite here
  instead of waiting for a slow round close to notice.
"""

from __future__ import annotations

import ast
import importlib.util
import json
import re
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from collections.abc import Iterator
    from types import ModuleType

REPO_ROOT = Path(__file__).resolve().parents[2]
RECORDS_DIR = REPO_ROOT / "docs" / "figures" / "run_records"
DEMO_DIR = REPO_ROOT / "tests" / "integration"
_CAPABILITY = re.compile(r"^CAPABILITY = \"(?P<stem>[a-z0-9_]+)\"$", re.MULTILINE)
_MIN_OWNERS = 5

# Owner modules opt in by declaring CAPABILITY; the record stem is derived
# from the declaration, so adding a claim-owning demo is a one-line change
# and cannot disagree with the record it names.
_OWNER_MODULES = tuple(
    sorted(DEMO_DIR.glob("test_demo_*.py")),
)


def _capabilities() -> dict[Path, str]:
    return {
        path: match.group("stem")
        for path in _OWNER_MODULES
        if (match := _CAPABILITY.search(path.read_text(encoding="utf-8")))
    }


def _records() -> dict[str, dict]:
    return {
        path.stem: json.loads(path.read_text(encoding="utf-8"))
        for path in sorted(RECORDS_DIR.glob("*.json"))
    }


def _load(path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(f"_claims_{path.stem}", path)
    assert spec is not None and spec.loader is not None, path
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_the_scan_actually_scans() -> None:
    """A lock over zero owners is a lock that cannot fail (§0)."""
    owners = _capabilities()
    assert len(owners) >= _MIN_OWNERS, (
        f"only {len(owners)} demo(s) declare CAPABILITY; the ownership "
        f"population fell below {_MIN_OWNERS} — either a demo lost its "
        "claim function or this lock's floor is stale"
    )
    records = _records()
    for path, stem in owners.items():
        assert stem in records, f"{path.name} claims {stem}, which has no record"
        assert records[stem]["demo_test"] == path.relative_to(REPO_ROOT).as_posix(), (
            f"{path.name} claims {stem}, but that record names "
            f"{records[stem]['demo_test']} as its owner"
        )


def _string_literals(path: Path) -> set[str]:
    """Every string constant in a module except its docstrings.

    Docstrings are excluded because a lock's *prose* naming a record is not a
    read of it: `test_gallery_provenance_lock` explains the `d24` provenance
    defect in its module docstring and asserts nothing about the record.
    """
    tree = ast.parse(path.read_text(encoding="utf-8"))
    docstrings = {
        id(node.body[0].value)
        for node in ast.walk(tree)
        if isinstance(
            node, ast.Module | ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef
        )
        and node.body
        and isinstance(node.body[0], ast.Expr)
        and isinstance(node.body[0].value, ast.Constant)
        and isinstance(node.body[0].value.value, str)
    }
    return {
        node.value
        for node in ast.walk(tree)
        if isinstance(node, ast.Constant) and isinstance(node.value, str)
        if id(node) not in docstrings
    }


def test_no_test_reads_another_demos_record() -> None:
    """The cross-claim class, closed: a record is readable by its owner.

    Deliberately scoped to the *record file name* rather than the capability
    stem: a demo that computes its own cells is free to mention a stem in
    prose, and each record's `demo_test` field is what makes the ownership
    check exact instead of a naming convention.
    """
    records = _records()
    for path in sorted(REPO_ROOT.glob("tests/**/*.py")):
        if path == Path(__file__).resolve():
            continue  # this lock names stems in its own prose, by design
        source = path.read_text(encoding="utf-8")
        if not any(stem in source for stem in records):
            continue  # substring pre-filter: parsing every test module is not free
        literals = _string_literals(path)
        for stem, record in records.items():
            if stem not in literals:
                continue
            owner = REPO_ROOT / record["demo_test"]
            assert path == owner, (
                f"{path.relative_to(REPO_ROOT)} references the {stem} record, "
                f"which {record['demo_test']} owns. A demo asserting on "
                "another demo's committed record is a cross-claim lock with no "
                "invalidation path — it went red for nineteen days for exactly "
                "that reason (TODO35 §10.2). Move the claim into the owner's "
                "assert_claims."
            )


@pytest.fixture(scope="module")
def owners() -> Iterator[dict[str, tuple[Path, ModuleType]]]:
    yield {
        stem: (path, _load(path))
        for path, stem in _capabilities().items()
        if "assert_claims" in path.read_text(encoding="utf-8")
    }


def test_owner_claims_hold_against_the_committed_record(
    owners: dict[str, tuple[Path, ModuleType]],
) -> None:
    """The owner's own claims, run against the owner's own committed record.

    This is the replacement for F4's copies: the same assertions, owned by
    the demo that emits the data, and evaluated in the fast lane rather than
    behind a `slow` marker nobody runs.
    """
    records = _records()
    assert owners, "no demo exposes assert_claims; the claim population is empty"
    for stem, (path, module) in sorted(owners.items()):
        claims: object = getattr(module, "assert_claims")
        assert callable(claims), f"{path.name}: assert_claims is not callable"
        claims(records[stem]["data"])  # pyright: ignore[reportNotCallable]
