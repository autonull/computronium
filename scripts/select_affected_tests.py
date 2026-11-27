"""The test files a working-tree change can reach, for the affected suite.

Reads the changed paths (staged, unstaged and untracked Python files), maps
each library file to its dotted module, then scans ``tests/`` for a test file
that imports that module *or* its parent package (a package ``__init__``
re-exports, so a change under ``domains/base.py`` reaches a test importing
``computronium.domains``).

Prints one test path per line. An empty list means the change reaches no
test file: run the fast suite instead (``scripts/run_fast_gates.sh``).

Usage::

    uv run python scripts/select_affected_tests.py            # working tree
    uv run python scripts/select_affected_tests.py --rev HEAD~1
"""

from __future__ import annotations

import argparse
import ast
import subprocess  # ruff: ignore[suspicious-subprocess-import] - git is the local tool
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
LIBRARY = "computronium"
TESTS = "tests"


def _changed(rev: str | None) -> list[Path]:
    """Changed Python paths: the working tree, or one revision's diff."""
    if rev is None:
        out = subprocess.run(  # ruff: ignore[subprocess-without-shell-equals-true] - the command is fixed
            [  # ruff: ignore[start-process-with-partial-path] - git is on the PATH
                "git",
                "status",
                "--porcelain",
                "--untracked-files=all",
            ],
            cwd=REPO,
            capture_output=True,
            text=True,
            check=True,
        ).stdout
        paths = [
            line[3:].strip()
            for line in out.splitlines()
            if line[3:].strip().endswith(".py")
        ]
    else:
        out = subprocess.run(  # ruff: ignore[subprocess-without-shell-equals-true] - the command is fixed
            [  # ruff: ignore[start-process-with-partial-path] - git is on the PATH
                "git",
                "diff",
                "--name-only",
                rev,
            ],
            cwd=REPO,
            capture_output=True,
            text=True,
            check=True,
        ).stdout
        paths = [line for line in out.splitlines() if line.endswith(".py")]
    return [REPO / path for path in paths]


def _module(path: Path) -> str:
    """The dotted module a library file defines."""
    relative = path.relative_to(REPO).with_suffix("")
    parts = list(relative.parts)
    if parts and parts[-1] == "__init__":
        parts.pop()
    return ".".join(parts)


def _reaches(module: str) -> set[str]:
    """The module and its parent packages: a package re-export is a reach.

    The top-level package is excluded: every test imports something under it,
    so counting it would select the whole suite for every change.
    """
    parts = module.split(".")
    return {".".join(parts[:i]) for i in range(2, len(parts) + 1)}


def _imports(path: Path) -> set[str]:
    """Every ``computronium.*`` module a test imports, by name."""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except SyntaxError, UnicodeDecodeError:
        return set()
    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            found.add(node.module)
        elif isinstance(node, ast.Import):
            found |= {alias.name for alias in node.names}
    return {name for name in found if name.startswith(f"{LIBRARY}.")}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rev", default=None, help="diff against this revision")
    args = parser.parse_args()

    changed = [path for path in _changed(args.rev) if path.is_file()]
    if not changed:
        print("the change is not a Python file change", file=sys.stderr)
        return 0
    targets = set()
    for path in changed:
        relative = path.relative_to(REPO)
        if relative.parts[0] != LIBRARY:
            continue
        targets |= _reaches(_module(path))

    selected: list[str] = []
    for test in sorted((REPO / TESTS).rglob("test_*.py")):
        imports = _imports(test)
        if any(
            name == target or name.startswith(f"{target}.")
            for name in imports
            for target in targets
        ):
            selected.append(str(test.relative_to(REPO)))

    print("\n".join(selected))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
