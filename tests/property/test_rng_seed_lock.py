"""TODO34 §1.5 — determinism ratchet: no *new* unseeded value assertions.

A test that draws from the global torch RNG and then asserts a number is
unreproducible, and under ``-n 4`` each worker holds its own stream, so a
failure cannot be re-run to the same inputs. Two of the defects in TODO34
§0 surfaced only because settle work shifted the global stream.

Scope is deliberately narrow, because a lock with false positives gets
switched off (the §2.5 lesson). A test is flagged only when *all* hold:

* it calls a global ``torch.<rand*|randint|randperm|normal>`` directly,
* nothing in the function or the module body seeds a generator, and
* it asserts on a *number* — an ordered comparison, ``allclose``,
  ``isclose`` or ``pytest.approx``.

Shape-only tests are exempt: whether ``torch.randn(3, 4)`` has shape
``(3, 4)`` does not depend on the draw. That exemption is why the
unflagged population is large (334 unseeded tests) while the flagged one
was not (116, across 42 files).

The baseline is now **empty**: all 116 were seeded and the count is zero,
so this is a ban rather than a ratchet. ``_BASELINE`` is kept because the
staleness assertion that keeps a ratchet honest is the same assertion, and
a non-empty baseline here is by definition a regression.

Because a zero baseline makes the §0.6 population guard vacuous — the
lock would "pass" if the scanner stopped seeing anything at all — the
guard is re-expressed against the *scan population* (2,773 test functions,
463 of which draw from the global RNG) and ``test_scan_classifies``
below is the probe-the-probe that pins the classifier itself.
"""

import ast
from pathlib import Path
from typing import Final

import pytest

TESTS_DIR: Final = Path(__file__).resolve().parents[1]

_RNG_CALLS: Final = frozenset({
    "rand",
    "rand_like",
    "randint",
    "randint_like",
    "randn",
    "randn_like",
    "randperm",
    "normal",
})
_SEED_CALLS: Final = ("manual_seed", "set_rng_state", "Generator(", "fork_rng")
_ORDERED_CMP: Final = frozenset({"Lt", "LtE", "Gt", "GtE"})
_TOLERANCE_CMP: Final = ("allclose", "isclose", "approx")

_BASELINE: dict[str, tuple[str, ...]] = {}


def _callees(fn: ast.AST) -> list[str]:
    return [
        ast.unparse(node.func) for node in ast.walk(fn) if isinstance(node, ast.Call)
    ]


def _seeds(stream: str) -> bool:
    return any(marker in stream for marker in _SEED_CALLS)


def _asserts_on_numbers(fn: ast.AST) -> bool:
    for node in ast.walk(fn):
        if not isinstance(node, ast.Assert):
            continue
        if isinstance(node.test, ast.Compare) and any(
            type(op).__name__ in _ORDERED_CMP for op in node.test.ops
        ):
            return True
        if any(marker in ast.unparse(node.test) for marker in _TOLERANCE_CMP):
            return True
    return False


def _qualified(fn: ast.AST, cls: str | None) -> str:
    name = fn.name  # type: ignore[attr-defined]
    return f"{cls}::{name}" if cls else name


def _scan_tests(path: Path) -> tuple[bool, dict[str, list[str]]]:
    """Return (module_seeds, {qualified test name: unseeded RNG calls})."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    module_seeds = any(
        _seeds(ast.unparse(node))
        for node in tree.body
        if isinstance(node, (ast.Call, ast.Expr))
    )
    found: dict[str, list[str]] = {}
    for cls in (n for n in tree.body if isinstance(n, ast.ClassDef)):
        for fn in cls.body:
            if isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)) and (
                fn.name.startswith("test_")
            ):
                _record(found, _qualified(fn, cls.name), fn, module_seeds)
    for fn in (
        n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
    ):
        if fn.name.startswith("test_"):
            _record(found, _qualified(fn, None), fn, module_seeds)
    return module_seeds, found


def _record(
    into: dict[str, list[str]], key: str, fn: ast.AST, module_seeds: bool
) -> None:
    if module_seeds:
        return
    callees = _callees(fn)
    if _seeds(ast.unparse(fn)):
        return
    unseeded = [
        callee
        for callee in callees
        if callee.startswith("torch.") and callee.rsplit(".", 1)[-1] in _RNG_CALLS
    ]
    if unseeded and _asserts_on_numbers(fn):
        into[key] = unseeded


def _unseeded() -> dict[str, tuple[str, ...]]:
    found: dict[str, tuple[str, ...]] = {}
    for path in sorted(TESTS_DIR.rglob("test_*.py")):
        _module_seeds, per_file = _scan_tests(path)
        if per_file:
            found[str(path.relative_to(TESTS_DIR.parent))] = tuple(sorted(per_file))
    return found


def test_no_new_unseeded_value_assertions() -> None:
    unseeded = _unseeded()
    baseline = {path: set(names) for path, names in _BASELINE.items()}
    new = {
        path: sorted(set(names) - baseline.get(path, set()))
        for path, names in unseeded.items()
    }
    new = {path: names for path, names in new.items() if names}
    assert not new, (
        "unseeded value assertions added (TODO34 §1.5): seed the RNG locally with "
        f"`torch.manual_seed(0)` before the first draw. Offenders: {new}"
    )
    stale = sorted(set(baseline) - set(unseeded))
    assert not stale, (
        f"baseline entries no longer flagged — delete them from _BASELINE: {stale}"
    )


def test_scan_population_is_non_trivial() -> None:
    """The §0.6 lesson: a lock that silently scans nothing is not a lock.

    With an empty baseline the flagged count is legitimately zero, so the
    guard has to measure the *population the classifier runs over*: if a
    rename or a path change stopped the scan resolving tests, the ban above
    would pass for the wrong reason.
    """
    scanned = drawn = 0
    for path in sorted(TESTS_DIR.rglob("test_*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and (
                node.name.startswith("test_")
            ):
                scanned += 1
                if any(
                    callee.startswith("torch.")
                    and callee.rsplit(".", 1)[-1] in _RNG_CALLS
                    for callee in _callees(node)
                ):
                    drawn += 1
    assert scanned >= 2000, f"scan resolved only {scanned} test functions"
    assert drawn >= 300, f"scan resolved only {drawn} global-RNG tests"


@pytest.mark.parametrize(
    ("source", "flagged"),
    [
        pytest.param(
            "def test_x():\n"
            "    torch.manual_seed(0)\n"
            "    y = torch.randn(4)\n"
            "    assert y.mean() > 0.5\n",
            False,
            id="locally_seeded",
        ),
        pytest.param(
            "def test_x():\n    y = torch.randn(4)\n    assert y.shape == (4,)\n",
            False,
            id="shape_only",
        ),
        pytest.param(
            "torch.manual_seed(0)\n\n\ndef test_x():\n"
            "    y = torch.randn(4)\n"
            "    assert y.mean() < 10\n",
            False,
            id="module_seeded",
        ),
        pytest.param(
            "def test_x():\n    y = torch.randn(4)\n    assert y.mean() < 10\n",
            True,
            id="flagged",
        ),
    ],
)
def test_scan_classifies(source: str, flagged: bool, tmp_path: Path) -> None:
    path = tmp_path / "test_probe.py"
    path.write_text(source, encoding="utf-8")
    _module_seeds, found = _scan_tests(path)
    assert bool(found) is flagged
