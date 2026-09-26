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
  ``_LAZY`` -- they have their own locks), star-import shims, whose names are
  not statically derivable at all, and ``TYPE_CHECKING``-block imports, which
  are pyright's population and are checked as such by the widened per-commit
  gate. What is left is the class that has no other gate: an import that
  fails at runtime.

The lock covers the whole of ``computronium/``. It was scoped to ``core`` +
``ontology`` for two rounds because 13 files failed it, and scoping a lock to
dodge known failures is the arrangement TODO35 §0 warns about.
``cli/export_trained_kernel.py`` was the last holdout; it is now a documented
refusal that names its own blocker rather than an ``ImportError`` from a
deleted name, so the exemption is gone with it.
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
    ]
    assert missing == [], (
        f"{len(missing)} imports name a symbol the target module does not "
        f"define — each is an ImportError on the path that takes it:\n"
        + "\n".join(missing)
    )
