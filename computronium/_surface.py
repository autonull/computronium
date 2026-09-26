"""Import-time verification of the package's declared public surface.

The package publishes three things it can therefore be held to: ``__all__``,
the lazy attribute map behind it, and the modules ``README.md`` documents as
runnable entry points. All three rot silently -- a name in ``__all__`` that
nothing defines, a lazy target that raises on first access, a documented
``python -m`` module that cannot be imported -- because nothing in the tree
imports the surface to find out.

So the surface checks itself, here, at import time: every existing test that
imports ``computronium`` inherits the guard. Nothing is executed to check it
(a name's presence is a property of the file that would define it), which
keeps the check in the tens of milliseconds.

Excluded by construction, and why:

* ``__init__`` re-export surfaces resolve, because a re-export is itself an
  import and the target is checked the same way.
* Star imports and ``importlib`` attribute access are not statically
  derivable, so they are reported as skipped rather than resolved.
* ``TYPE_CHECKING``-only imports are pyright's population, not the runtime's.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from functools import cache, lru_cache
from pathlib import Path
from typing import TYPE_CHECKING, Final

if TYPE_CHECKING:
    from collections.abc import Iterable

__all__ = [
    "PublicSurfaceError",
    "assert_public_surface",
    "bound_names",
    "documented_entry_points",
    "surface_problems",
]

_ROOT: Final = Path(__file__).resolve().parent
_PACKAGE: Final = _ROOT.name
_README: Final = _ROOT.parent / "README.md"
_DOC_PATH: Final = re.compile(rf"`({re.escape(_PACKAGE)}/[\w./]+\.py)`")
_DOC_MODULE: Final = re.compile(rf"\b{re.escape(_PACKAGE)}(?:\.[A-Za-z_]\w*)+")
_PYTHON_M: Final = re.compile(
    rf"python -m\s+({re.escape(_PACKAGE)}(?:\.[A-Za-z_]\w*)+)"
)


class PublicSurfaceError(ImportError):
    """The package's declared public surface does not resolve."""


@dataclass(frozen=True, slots=True)
class Import:
    """One ``from <module> import <names>`` statement, as written."""

    module: str
    names: tuple[str, ...]
    wildcard: bool


@lru_cache(maxsize=1)
def _readme_text() -> str | None:
    """The repository README, or ``None`` when running from a wheel."""
    return _README.read_text(encoding="utf-8") if _README.is_file() else None


@cache
def module_path(module: str) -> Path | None:
    """The file that would define ``module``, resolved without importing it."""
    prefix = f"{_PACKAGE}."
    if not module.startswith(prefix):
        return None
    base = _ROOT.joinpath(*module[len(prefix) :].split("."))
    for candidate in (base.with_suffix(".py"), base / "__init__.py"):
        if candidate.is_file():
            return candidate
    return None


_IF_TYPE_CHECKING: Final = re.compile(r"^([ \t]*)if\s+TYPE_CHECKING\b")
_DEFINITION: Final = re.compile(
    r"^(?:async\s+def|def|class|type)\s+(\w+)|^(\w+)\s*(?::[^=\n]*)?=(?!=)",
    re.MULTILINE,
)
_FROM: Final = re.compile(
    r"^(?P<indent>[ \t]*)from\s+(?P<module>[.\w]+)\s+import\s*"
    r"(?P<names>\((?:[^)]*)\)|[^\n]*)",
    re.MULTILINE,
)


@cache
def _scanned(path: Path) -> tuple[frozenset[str], tuple[Import, ...]]:
    """The names ``path`` binds, and the computronium imports it makes.

    Scanned by pattern rather than by ``ast`` or ``tokenize``: this runs on
    every ``import computronium``, and parsing the ~25 modules the lazy map
    points at costs 20x what three regex passes over them cost. The patterns
    cover the three ways a module binds a name it exports -- a definition, an
    assignment, and an import (at any indent, so a ``try``-guarded re-export
    counts). What they do not see is a name bound by ``globals()`` or a star
    import, which is also what no static check can see.
    """
    source = path.read_text(encoding="utf-8")
    names = frozenset(
        name
        for match in _DEFINITION.finditer(source)
        if (name := match.group(1) or match.group(2))
    )
    return names, tuple(_from_imports(source))


def _from_imports(source: str) -> list[Import]:
    """The ``from ... import ...`` statements that exist at runtime.

    Indent-tracked rather than parsed: only the ``if TYPE_CHECKING`` blocks
    have to be excluded, and they are excluded by comparing indents, which
    is why a function-local import is still seen (several of the imports this
    exists to check are function-local).
    """
    imports: list[Import] = []
    guarded_at: int | None = None
    for match in _FROM.finditer(source):
        indent = len(match.group("indent").expandtabs())
        if guarded_at is None and _IF_TYPE_CHECKING.match(source, match.start()):
            guarded_at = indent
            continue
        if guarded_at is not None:
            if indent > guarded_at:
                continue
            guarded_at = None
        raw = re.sub(r"#.*", "", match.group("names"))
        bound = tuple(
            name
            for part in (piece.strip() for piece in raw.strip("() \n").split(","))
            for name in (part.split(" as ")[-1].strip(),)
            if name
        )
        imports.append(Import(match.group("module"), bound, "*" in bound))
    return imports


def _defines(module: str, name: str) -> bool:
    """Does ``module`` bind ``name``? Re-exports count: they are imports."""
    path = module_path(module)
    return path is not None and name in bound_names(path)


def bound_names(path: Path) -> frozenset[str]:
    """Every name ``path`` binds, imports included."""
    names, imports = _scanned(path)
    return frozenset(names | {name for statement in imports for name in statement.names})


@lru_cache(maxsize=1)
def documented_entry_points() -> tuple[tuple[str, ...], tuple[str, ...]]:
    """``(module_paths, module_dotted)`` the README documents as entry points.

    ``python -m`` invocations, backticked source paths and dotted references
    are all ways the README names a runnable module; the third is the
    weakest signal, so it is kept separate for the report.
    """
    text = _readme_text()
    if text is None:
        return (), ()
    paths = tuple(sorted(_DOC_PATH.findall(text)))
    dotted = tuple(
        sorted(
            {m.rstrip(".") for m in _DOC_MODULE.findall(text)}
            | set(_PYTHON_M.findall(text))
        )
    )
    return paths, dotted


def _lazy_problems(
    public: Iterable[str], lazy: dict[str, tuple[str, str | None]], defined: set[str]
) -> list[str]:
    problems: list[str] = []
    declared = set(public)
    for name in sorted(declared - set(lazy) - defined):
        problems.append(f"{name} is in __all__ but nothing binds it")
    for name in sorted(set(lazy) - declared):
        problems.append(f"{name} is lazily imported but missing from __all__")
    for name, (module, attribute) in sorted(lazy.items()):
        if attribute is None:
            continue
        if not module.startswith(f"{_PACKAGE}."):
            continue
        if module_path(module) is None:
            problems.append(f"{name} maps to {module}, which does not exist")
        elif not _defines(module, attribute):
            problems.append(
                f"{name} maps to {module}.{attribute}, which is not defined"
            )
    return problems


def _documented_problems() -> list[str]:
    """README-named modules: they must exist, and their imports must resolve.

    The second half is the defect class ``F821`` cannot see -- ``from
    computronium.core.trainer import CoreTrainer`` is a valid import to a
    linter and an ``ImportError`` to a person running the documented command.
    """
    paths, dotted = documented_entry_points()
    problems: list[str] = []
    for relative in paths:
        if not (_ROOT.parent / relative).is_file():
            problems.append(f"README documents {relative}, which does not exist")
    for module in dotted:
        if module_path(module) is None:
            problems.append(f"README documents {module}, which is not a module")
    problems.extend(
        problem
        for relative in paths
        for problem in _entry_point_problems(_ROOT.parent / relative)
    )
    return problems


def _entry_point_problems(source: Path) -> list[str]:
    """Every unresolvable computronium import in one documented module."""
    if not source.is_file():
        return []
    relative = source.relative_to(_ROOT.parent)
    problems: list[str] = []
    for statement in _scanned(source)[1]:
        if not statement.module.startswith(f"{_PACKAGE}.") or statement.wildcard:
            continue
        if module_path(statement.module) is None:
            problems.append(
                f"{relative} imports {statement.module}, which does not exist"
            )
            continue
        problems.extend(
            f"{relative} imports {statement.module}.{name}, which is not defined there"
            for name in statement.names
            if not _defines(statement.module, name)
        )
    return problems


def surface_problems(
    public: Iterable[str],
    lazy: dict[str, tuple[str, str | None]],
    defined: set[str],
) -> list[str]:
    """Every way the declared surface fails to resolve, as readable lines."""
    return sorted({*_lazy_problems(public, lazy, defined), *_documented_problems()})


def assert_public_surface(
    public: Iterable[str],
    lazy: dict[str, tuple[str, str | None]],
    defined: set[str],
) -> None:
    """Raise :class:`PublicSurfaceError` unless the declared surface resolves.

    Called from the package's own ``__init__``, so every caller of every
    exported name is downstream of this check.
    """
    problems = surface_problems(public, lazy, defined)
    if problems:
        listed = "\n".join(f"  - {problem}" for problem in problems)
        raise PublicSurfaceError(
            f"{len(problems)} public-surface problem(s) in {_PACKAGE}:\n{listed}"
        )
