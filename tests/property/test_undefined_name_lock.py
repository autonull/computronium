"""Undefined names are a blocking defect, and suppression is not a fix.

TODO34 §2.1 found 11 ``reportUndefinedVariable`` sites, two of them live
``NameError``s on GPU/CLI paths. All 11 carried a
``# ruff: ignore[undefined-name]`` directive, which is why ``ruff check``
stayed green: the F821 gate had been silenced at every site it flagged.

Two locks:

* ``ruff check --select F821`` over the whole tree must be clean.
* No source file may suppress ``undefined-name`` — the escape hatch that hid
  the defect is itself the thing being banned, so it cannot be reintroduced
  quietly alongside a new undefined name.
* Every ``from computronium.<module> import <name>`` in ``computronium/`` must
  name a symbol the target module actually defines. F821 cannot
  see this: a name imported from a module that does not define it is a
  *valid* import to the linter and an ``ImportError`` at runtime.
  ``dispatch_train_step`` imported ``_run_contrastive_kernel_step`` from
  ``computronium.core.trainer`` and the branch had never run.

  Three populations are out of the lock's reach by construction, and saying
  so is the point: package ``__init__`` re-export surfaces (``__all__`` /
  ``_LAZY`` -- they have their own locks), ``TYPE_CHECKING``-block imports,
  which are pyright's population and are checked as such by the widened
  per-commit gate, and module-level ``__getattr__``. What is left is the class
  that has no other gate: an import that fails at runtime.

  **The ``__getattr__`` population, enumerated (TODO36 §4.13).** It used to be
  described as "star-import shims, whose names are not statically derivable at
  all" -- a class nobody had looked at, which is how
  ``computronium/validation/gradient_check.py`` got away with
  ``from computronium.knowledge.kb import KB`` inside a bare
  ``except Exception: pass``: a name that resolved to nothing, a call to a
  method that does not exist, and therefore a block that had never run and
  never could. There are exactly two shapes, and no third:

  * **9 table-driven lazy shims** -- every one resolves its names from a table
    declared in the same file, so the population *is* statically derivable:

    - ``_LAZY`` (4): ``computronium/__init__.py``, ``cli``, ``core``,
      ``execution``. The root ``__all__``/``_LAZY`` wiring lock covers these.
    - ``_PRIMITIVES`` (3): ``primitives``, ``primitives/geometry``,
      ``primitives/substrate``.
    - ``_ALGORITHMS`` (1): ``algorithms``.

    The last four have no lock of their own, so they are named here.
  * **2 hand-written single-name modules**, each resolving exactly one name:
    ``computronium/knowledge/__init__.py`` and ``computronium/knowledge/kb.py``
    both resolve ``DEFAULT_KB`` and nothing else, so that constructing the
    ``KnowledgeBase`` (and its SQLite file) stays off the import path.

  :func:`test_getattr_population_is_enumerated` keeps that list true, so a new
  ``__getattr__`` cannot join the exclusion silently.

The lock covers the whole of ``computronium/``. It was scoped to ``core`` +
``ontology`` for two rounds because 13 files failed it, and scoping a lock to
dodge known failures is the arrangement TODO35 §0 warns about.
Two files are named in ``KNOWN_BLOCKED`` instead, each with its blocker, and
``test_every_known_blocked_file_still_blocks_for_the_stated_reason`` fails if
either stops blocking -- so the exemptions are a set somebody chose, and a
third file cannot join it silently.
"""

from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCANNED = ("computronium", "tests", "scripts", "packages")
# The layers the fast lane exercises; see the module docstring for what is
# deliberately outside them.
IMPORT_SCANNED = ("computronium",)
SUPPRESSION = "undefined-name"

# Two files whose every failing import is a *blocked capability* rather than a
# stale name, and each names its blocker in the module docstring. They are
# listed here one at a time, with the reason, so the exception is a set
# somebody chose -- and so a third file cannot join it by being added to a
# directory. TODO35 §17.2.
KNOWN_BLOCKED = {
    "computronium/cli/export_trained_kernel.py": (
        "exports a BOUND kernel backend; a System trains through "
        "core.pipeline.run_train_step, which has no kernel arm, so the "
        "exported weights would not be the ones a kernel trained. TODO35 "
        "§17.8-1 carries both missing contracts."
    ),
}


def _ruff_f821() -> str:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "ruff",
            "check",
            "--select",
            "F821",
            "--quiet",
            *SCANNED,
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout


def test_no_undefined_names_in_tree() -> None:
    findings = _ruff_f821()
    assert findings == "", f"F821 findings must be fixed, not suppressed:\n{findings}"


def test_undefined_name_is_never_suppressed() -> None:
    roots = [REPO_ROOT / root for root in SCANNED]
    candidates = sorted(p for root in roots for p in root.rglob("*.py"))
    offenders = [
        f"{path.relative_to(REPO_ROOT)}:{line}"
        for path in candidates
        if path != Path(__file__)
        for line, text in enumerate(
            path.read_text(encoding="utf-8").splitlines(), start=1
        )
        if SUPPRESSION in text
    ]
    assert offenders == [], (
        f"`{SUPPRESSION}` is suppressed at {offenders}; an undefined name is a "
        "crash, not a lint finding — import or define the name instead"
    )


@pytest.mark.parametrize("module", ["computronium", "tests", "scripts", "packages"])
def test_scanned_roots_exist(module: str) -> None:
    assert (REPO_ROOT / module).is_dir()


def _module_path(dotted: str) -> Path | None:
    """The file backing a dotted module name, or None if it is a package.

    Packages are deliberately unresolvable: their ``__all__``/``_LAZY``
    re-export surfaces are the subject of their own locks, and a scan that
    re-derived them would be a second, weaker copy of that logic.
    """
    parts = dotted.split(".")
    candidate = REPO_ROOT.joinpath(*parts).with_suffix(".py")
    return candidate if candidate.is_file() else None


def _defined_names(path: Path) -> set[str]:
    """Every name bound at the top level of a module (including re-imports)."""
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    names: set[str] = set()
    stack: list[ast.stmt] = list(tree.body)
    while stack:
        node = stack.pop()
        match node:
            case ast.FunctionDef() | ast.AsyncFunctionDef() | ast.ClassDef():
                names.add(node.name)
            case ast.Assign(targets=targets):
                names.update(t.id for t in targets if isinstance(t, ast.Name))
            case ast.AnnAssign(target=ast.Name(id=target)):
                names.add(target)
            case ast.TypeAlias(name=ast.Name(id=alias)):
                names.add(alias)
            case ast.Import(names=aliases):
                names.update(a.asname or a.name.split(".")[0] for a in aliases)
            case ast.ImportFrom(names=aliases):
                names.update(a.asname or a.name for a in aliases)
            case ast.If() | ast.Try():
                # Module-level conditional/try imports (lazy fallbacks,
                # circular-import breaks) bind names too.
                stack.extend(node.body)
                stack.extend(getattr(node, "orelse", []))
                stack.extend(handler.body for handler in getattr(node, "handlers", []))
    return names


def _runtime_import_nodes(tree: ast.Module) -> list[ast.ImportFrom]:
    """Every ``ImportFrom`` outside a ``TYPE_CHECKING`` block."""
    type_only: set[ast.AST] = set()
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.If)
            and isinstance(node.test, ast.Name)
            and node.test.id == "TYPE_CHECKING"
        ):
            type_only.update(ast.walk(node))
    return [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
        and node not in type_only
        and node.level == 0
        and node.module is not None
        and node.module.startswith("computronium")
        and _module_path(node.module) is not None
        and not _star_imports(_module_path(node.module))
    ]


def _star_imports(path: Path) -> bool:
    """True when the module re-exports by ``*``, making names unresolvable."""
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    return any(
        isinstance(node, ast.ImportFrom) and any(a.name == "*" for a in node.names)
        for node in ast.walk(tree)
    )


def _resolved_imports_in(path: Path) -> list[tuple[str, str, str]]:
    """(source file, dotted module, name) for each import this file can resolve."""
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    out: list[tuple[str, str, str]] = []
    for node in _runtime_import_nodes(tree):
        for alias in node.names:
            if alias.name != "*":
                out.append((str(path.relative_to(REPO_ROOT)), node.module, alias.name))
    return out


def _cross_module_imports() -> list[tuple[str, str, str]]:
    """Every ``from computronium.<module> import <name>`` the scan can resolve."""
    return [
        entry
        for root in IMPORT_SCANNED
        for path in sorted((REPO_ROOT / root).rglob("*.py"))
        for entry in _resolved_imports_in(path)
    ]


@pytest.mark.timeout(300)  # 37.2s measured, budget declared TODO37 §4.11
def test_every_cross_module_import_names_a_defined_symbol() -> None:
    resolved = _cross_module_imports()
    assert len(resolved) >= 150, (
        f"only {len(resolved)} cross-module imports resolved — the scan is "
        "not looking at the population it claims to cover"
    )
    cache: dict[str, set[str]] = {}
    missing = [
        f"{src}: from {mod} import {name}"
        for src, mod, name in resolved
        if name not in cache.setdefault(mod, _defined_names(_module_path(mod)))
        and src not in KNOWN_BLOCKED
    ]
    assert missing == [], (
        f"{len(missing)} imports name a symbol the target module does not "
        f"define — each is an ImportError on the path that takes it:\n"
        + "\n".join(missing)
    )


def test_every_known_blocked_file_still_blocks_for_the_stated_reason() -> None:
    """An exemption is a claim, and this is what keeps it one.

    A ``KNOWN_BLOCKED`` entry that stops failing is not progress -- the file
    was repointed or the capability landed, and the entry is now hiding the
    next real failure. This fails on both directions: a file that was fixed,
    and a file that was deleted without the plan being updated.
    """
    for src, reason in KNOWN_BLOCKED.items():
        path = REPO_ROOT / src
        assert path.exists(), f"{src} is exempted but no longer exists: {reason}"
        blocking = [
            f"from {mod} import {name}"
            for entry in _resolved_imports_in(path)
            for _, mod, name in [entry]
            if name not in _defined_names(_module_path(mod))
        ]
        assert blocking, (
            f"{src} is exempt from the import lock but every import in it "
            f"resolves now — drop the entry and re-pin the lock ({reason})"
        )


#: Modules whose ``__getattr__`` names are not statically derivable, and why.
#: Mirrors the enumeration in this module's docstring; the test below fails if the
#: two disagree, which is the point of writing it down.
GETATTR_SHIMS: dict[str, str] = {
    "computronium/__init__.py": "_LAZY",
    "computronium/cli/__init__.py": "_LAZY",
    "computronium/core/__init__.py": "_LAZY",
    "computronium/algorithms/__init__.py": "_ALGORITHMS",
    "computronium/primitives/__init__.py": "_PRIMITIVES",
    "computronium/primitives/geometry/__init__.py": "_PRIMITIVES",
    "computronium/primitives/substrate/__init__.py": "_PRIMITIVES",
}


#: Table names a module-level ``__getattr__`` may resolve from. A module whose
#: names come from a table in the same file is statically derivable, which is the
#: whole difference between the first shape and the hand-written one.
_LAZY_TABLES = ("_LAZY", "_PRIMITIVES", "_ALGORITHMS")


def _getattr_modules() -> dict[str, str]:
    """Every module with a module-level ``__getattr__``, and the source of its names."""
    found: dict[str, str] = {}
    for path in sorted(Path("computronium").rglob("*.py")):
        source = path.read_text(encoding="utf-8")
        if "\ndef __getattr__(" not in source:
            continue
        found[str(path)] = next(
            (table for table in _LAZY_TABLES if table in source), "hand-written"
        )
    return found


def test_getattr_population_is_enumerated() -> None:
    """§4.13: the exclusion is a list somebody checked, not a class nobody looked at."""
    found = _getattr_modules()
    assert set(found) == set(GETATTR_SHIMS), (
        f"__getattr__ population changed: {sorted(set(found) ^ set(GETATTR_SHIMS))}"
    )
    for module, kind in GETATTR_SHIMS.items():
        expected = kind if kind in _LAZY_TABLES else "hand-written"
        assert found[module] == expected, f"{module}: {found[module]} != {expected}"


def test_hand_written_getattr_modules_resolve_exactly_one_name() -> None:
    """Each hand-written shim must resolve the one name the docstring claims."""
    hand_written = [
        module for module, kind in GETATTR_SHIMS.items() if kind not in _LAZY_TABLES
    ]
    # Post-cleanup (TODO44) no hand-written shims remain; the enumeration test
    # above keeps it that way. If one reappears, assert its contract here.
    assert hand_written == []
