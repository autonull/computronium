"""Structural ratchets on test quality (TODO34 §2.5).

Every defect in TODO34 §0 was caught by a human reading the output, not by
the suite. Four of them shared a shape: an assertion that could not fail.
This module makes that shape expensive to reintroduce.

Current rules:

* **No vacuous sole assertions.** ``assert isinstance(x, list)`` as a test's
  only assertion proves nothing when the return annotation already says
  ``-> list``. Asserting a *domain* type is exempt: "the registry factory
  returns an instance of the class the registry claims" is a real claim that
  no annotation makes.

  The plan also proposed banning a sole ``assert x is not None``. **Tried it
  and dropped it**: ``assert selected_experiment is None`` is how a dozen
  tests state "this lookup finds nothing", which is a stronger and more
  specific claim than a type check. Flagging it produced 14 false positives
  on first run, and a lock with false positives gets switched off. Banning
  ``is None`` needs return-type analysis to separate "restates a non-optional
  annotation" from "asserts a sentinel", which is §2.4's job, not this
  lock's.

Rules from §2.5 that are **deliberately not implemented here**, and why:

* *Unseeded RNG in value-asserting tests* — needs a dataflow judgement (does
  this test assert on a value derived from the draw?) that a heuristic would
  get wrong more often than it would catch. Left to §1.5.
* *Environment-dependent rendering asserts* — the failure mode is a terminal
  width, not a syntactic pattern. Left to the demos that pin it.
* *Asserting the opposite of a test's name* — the plan itself says "cheap to
  check by eye, and it happened (0.8)". Not automatable without an LLM; a
  regex here would be theatre.
"""

from __future__ import annotations

import ast
from pathlib import Path

TESTS_ROOT = Path(__file__).resolve().parents[1]

# Types whose presence an annotation already guarantees, so isinstance
# against them carries no information.
VACUOUS_TYPES = frozenset({
    "bool",
    "bytes",
    "complex",
    "dict",
    "float",
    "frozenset",
    "int",
    "list",
    "set",
    "str",
    "tuple",
})


def _sole_assertion(
    test: ast.FunctionDef | ast.AsyncFunctionDef,
) -> ast.Assert | None:
    """The test's only assert, if it has exactly one of its own.

    Assertions inside a function nested in ``test`` belong to that inner
    function: counting them here would both pollute the outer total and
    double-report the inner one.
    """
    nested: list[ast.AST] = []
    for node in ast.walk(test):
        if node is test:
            continue
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef | ast.Lambda):
            nested.extend(n for n in ast.walk(node) if isinstance(n, ast.Assert))
    owned = [
        n
        for n in ast.walk(test)
        if isinstance(n, ast.Assert) and not any(n is inner for inner in nested)
    ]
    return owned[0] if len(owned) == 1 else None


def _is_vacuous(assertion: ast.Assert) -> bool:
    node = assertion.test
    if isinstance(node, ast.Call):
        if not (isinstance(node.func, ast.Name) and node.func.id == "isinstance"):
            return False
        if len(node.args) != 2:
            return False
        target = node.args[1]
        return isinstance(target, ast.Name) and target.id in VACUOUS_TYPES
    return False


def _vacuous_in(source: str) -> list[int]:
    """Line numbers of vacuous sole assertions in a module's source."""
    tree = ast.parse(source)
    sites: list[int] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
            continue
        if node.name.startswith("_"):
            continue
        assertion = _sole_assertion(node)
        if assertion is not None and _is_vacuous(assertion):
            sites.append(assertion.lineno)
    return sites


def _vacuous_sites() -> list[str]:
    return [
        f"{path.relative_to(TESTS_ROOT)}:{line}"
        for path in sorted(TESTS_ROOT.rglob("test_*.py"))
        for line in _vacuous_in(path.read_text(encoding="utf-8"))
    ]


def test_no_vacuous_sole_assertion() -> None:
    sites = _vacuous_sites()
    assert sites == [], (
        f"sole assertions that cannot fail; assert the value, not its type: {sites}"
    )


def test_the_check_itself_detects_a_vacuous_assertion() -> None:
    """Guard the guard: the detector must flag the pattern it bans.

    Without this, a refactor that breaks ``_is_vacuous`` silently turns the
    lock into a no-op that always passes.
    """
    assert _vacuous_in("def t():\n    assert isinstance(x, list)\n") == [2]
    assert _vacuous_in("def t():\n    assert isinstance(x, Widget)\n") == []
    assert _vacuous_in("def t():\n    assert x is not None\n") == []
    assert _vacuous_in("def t():\n    assert x is None\n") == []
    assert _vacuous_in("def t():\n    assert isinstance(x, list)\n    assert y\n") == []


def test_sole_assertion_detector_handles_async_and_nested() -> None:
    assert _vacuous_in(
        "async def t():\n"
        "    async def inner():\n"
        "        assert isinstance(y, list)\n"
        "    await inner()\n"
    ) == [3]
