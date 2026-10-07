"""Does a capability row's verifying test exercise a mechanism, or only a name?

TODO46 §2.1. A capability row is evidence only if its ``verifying_test``

* names a test that exists in the source tree,
* *calls* a kernel entry point and asserts on the result — a test that imports a
  name or reads an attribute proves the name exists, not that anything works,
  and
* reaches an entry point with a call site outside its own module, because
  ``__all__`` membership is an offer rather than a use (TODO46 §2.0).

The judgement is made from the test's AST, so it costs no training and no wall
clock — the tier-0 dry run the plan's cost discipline requires. One
implementation, read by the capabilities listing and by
``tests/property/test_capability_evidence_lock.py``.
"""

from __future__ import annotations

import ast
import re
from dataclasses import dataclass
from functools import cached_property
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
PACKAGES_ROOT = REPO_ROOT / "packages"

# Vendored trees hold tens of thousands of .py files and would turn a ten-second
# judgement into a ten-minute one.
SOURCE_ROOTS = ("computronium", "tests", "scripts", "packages", "docs")
_SKIP = frozenset({
    ".venv",
    "build",
    "dist",
    "__pycache__",
    "node_modules",
    ".git",
    "site-packages",
})


@dataclass(frozen=True, slots=True)
class TestEvidence:
    """What one verifying test proves about the capability it backs."""

    exists: bool
    asserts: bool
    entry_point: str | None
    external_call_sites: int

    @property
    def mechanism(self) -> bool:
        """True when the test calls a kernel entry point and asserts on it."""
        return self.exists and self.asserts and self.external_call_sites >= 1

    @property
    def level(self) -> str:
        """``mechanism`` or ``shape`` — the label a listing renders."""
        return "mechanism" if self.mechanism else "shape"


class SourceIndex:
    """One read of the source tree, shared by every judgement."""

    def __init__(self, root: Path = REPO_ROOT) -> None:
        self._root = root

    @cached_property
    def _sources(self) -> tuple[tuple[Path, str, str], ...]:
        return tuple(
            (path, self.module_of(path), path.read_text(errors="ignore"))
            for path in sorted(
                p
                for name in SOURCE_ROOTS
                for p in (self._root / name).rglob("*.py")
                if not _SKIP & set(p.relative_to(self._root).parts)
            )
        )

    def module_of(self, path: Path) -> str:
        """Dotted module for a source file, ``''`` outside the kernel packages."""
        for base in (self._root / "computronium", PACKAGES_ROOT):
            try:
                rel = path.relative_to(base)
            except ValueError:
                continue
            if base is PACKAGES_ROOT and len(rel.parts) == 1:
                return ""
            return rel.with_suffix("").as_posix().replace("/", ".")
        return ""

    @cached_property
    def kernel_roots(self) -> frozenset[str]:
        """Import roots whose modules count as kernel: the repo and its packages."""
        roots = {"computronium"}
        for package in sorted(PACKAGES_ROOT.iterdir()):
            src = package / "src"
            if not src.is_dir():
                continue
            roots.update(
                path.name
                for path in sorted(src.iterdir())
                if (path / "__init__.py").is_file()
            )
        return frozenset(roots)

    @cached_property
    def _caller_index(self) -> dict[str, set[str]]:
        """Inverted index: callee name -> set of modules that call it."""
        from collections import defaultdict

        caller_index: dict[str, set[str]] = defaultdict(set)
        name_pattern = re.compile(r"\b([a-zA-Z_][a-zA-Z0-9_]*)\s*\(")
        for _, module, text in self._sources:
            for match in name_pattern.finditer(text):
                callee = match.group(1)
                caller_index[callee].add(module)
        return dict(caller_index)

    def external_call_sites(self, qualified: str) -> int:
        """Files outside the defining module that call ``qualified``."""
        name = qualified.rsplit(".", 1)[-1]
        defining = qualified.removesuffix(f".{name}")
        callers = self._caller_index.get(name, set())
        return sum(1 for module in callers if module != defining)


INDEX = SourceIndex()


def _locate(node_id: str) -> tuple[Path, str | None] | None:
    """Resolve a pytest node id to (file, function); a bare path is the module."""
    path_part, _, selector = node_id.partition("::")
    path = REPO_ROOT / path_part
    if not path.is_file():
        return None
    if not selector:
        return path, None
    return path, selector.rsplit("::", 1)[-1].split(".")[-1].split("[")[0]


def _kernel_aliases(
    tree: ast.Module, roots: frozenset[str], path: Path
) -> dict[str, str]:
    """Local name -> ``kernel.module.attr`` for kernel imports in a module.

    Relative imports of the test's own helpers are followed one level: a lock
    that asserts inside a shared helper is still asserting, and the helper is
    still part of the kernel's test surface.
    """
    aliases: dict[str, str] = {}
    siblings = path.parent
    for node in ast.walk(tree):
        match node:
            case ast.ImportFrom(module=module, names=names, level=level):
                if module is None:
                    continue
                target = (
                    f"{path.stem.removesuffix('test_')}{module}" if level else module
                )
                root = target.split(".")[0]
                relative = level and (siblings / target.split(".")[0]).is_file()
                if root in roots or relative:
                    for alias in names:
                        aliases[alias.asname or alias.name] = f"{target}.{alias.name}"
            case ast.Import(names=names):
                if any(n.name.split(".")[0] in roots for n in names):
                    for alias in names:
                        if alias.asname:
                            aliases[alias.asname] = alias.name
    return aliases


def _callees(node: ast.AST, aliases: dict[str, str]) -> set[str]:
    """Kernel-qualified callees of the statements under ``node``."""
    found: set[str] = set()
    for child in ast.walk(node):
        if not isinstance(child, ast.Call):
            continue
        match child.func:
            case ast.Name(id=name) if name in aliases:
                found.add(aliases[name])
            case ast.Attribute(value=ast.Name(id=prefix), attr=attr) if (
                prefix in aliases
            ):
                found.add(f"{aliases[prefix]}.{attr}")
            case _:
                pass
    return found


def _definitions(tree: ast.Module, name: str | None) -> list[ast.AST]:
    """The test bodies under test: one function, or every one in a module."""
    if name is not None:
        found = _definition(tree, name)
        return [found] if found is not None else []
    return [
        node
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
    ]


def _asserts(node: ast.AST) -> bool:
    """``assert``, or a ``pytest.raises``/``pytest.warns`` block — both are checks."""
    for child in ast.walk(node):
        if isinstance(child, ast.Assert):
            return True
        if (
            isinstance(child, ast.Call)
            and isinstance(child.func, ast.Attribute)
            and child.func.attr in {"raises", "warns"}
            and isinstance(child.func.value, ast.Name)
            and child.func.value.id == "pytest"
        ):
            return True
    return False


def _fixtures(tree: ast.Module) -> dict[str, ast.AST]:
    """Fixture name -> the function body it yields, for the test's own module."""
    found: dict[str, ast.AST] = {}
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if any(
            "fixture" in ast.dump(dec) for dec in node.decorator_list
        ) or node.name.startswith("_"):
            found.setdefault(node.name, node)
    return found


def _definition(tree: ast.Module, name: str) -> ast.AST | None:
    return next(
        (
            node
            for node in ast.walk(tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
            and node.name == name
        ),
        None,
    )


def evidence_for(
    verifying_test: str | None, index: SourceIndex = INDEX
) -> TestEvidence:
    """Judge one ``verifying_test`` node id: mechanism evidence or a name check."""
    located = _locate(verifying_test or "")
    if located is None:
        return TestEvidence(False, False, None, 0)
    path, name = located
    tree = ast.parse(path.read_text())
    bodies = _definitions(tree, name)
    if not bodies:
        return TestEvidence(False, False, None, 0)
    aliases = _kernel_aliases(tree, index.kernel_roots, path)
    fixtures = _fixtures(tree)
    best: tuple[int, str] | None = None
    asserts = False
    for body in bodies:
        requested = (
            {arg.arg for arg in body.args.args}
            if isinstance(body, (ast.FunctionDef, ast.AsyncFunctionDef))
            else set()
        )
        yieldable = [
            body,
            *(fixtures[arg] for arg in sorted(requested & fixtures.keys())),
        ]
        for part in yieldable:
            asserts = asserts or _asserts(part)
            for callee in sorted(_callees(part, aliases)):
                sites = index.external_call_sites(callee)
                if best is None or sites > best[0]:
                    best = (sites, callee)
    return TestEvidence(
        exists=True,
        asserts=asserts,
        entry_point=best[1] if best else None,
        external_call_sites=best[0] if best else 0,
    )


__all__ = ["INDEX", "SourceIndex", "TestEvidence", "evidence_for"]
