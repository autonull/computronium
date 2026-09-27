"""Session-scoped fixtures for acceleration tests."""

import ast
from pathlib import Path

import pytest

PACKAGE = Path(__file__).resolve().parents[2] / "computronium" / "acceleration"
REPO = PACKAGE.parents[1]


def _parse(path: Path) -> ast.Module:
    return ast.parse(path.read_text(encoding="utf-8"))


def _exported_twins() -> dict[str, Path]:
    modules = [PACKAGE / "contrastive_primitives.py", PACKAGE / "kernels.py"]
    modules += sorted(PACKAGE.glob("*_kernels.py"))
    twins: dict[str, Path] = {}
    for module in modules:
        for node in _parse(module).body:
            if isinstance(
                node, (ast.FunctionDef, ast.ClassDef)
            ) and not node.name.startswith("_"):
                twins[node.name] = module
    return twins


def _compute_uncalled_twins() -> set[str]:
    """Compute the set of uncalled exported twins (session-scoped, runs once).

    This is the expensive AST walk over the entire repo. Doing it once per
    session instead of per-test saves ~120s on targeted runs.
    """
    from computronium.acceleration import get_algorithm_kernels

    bound = set(get_algorithm_kernels().keys())
    twins = _exported_twins()
    used: set[str] = set()
    skip_dirs = {".venv", "build", "__pycache__", ".pytest_cache", ".git"}
    for path in REPO.rglob("*.py"):
        if any(skip in path.parts for skip in skip_dirs):
            continue
        try:
            tree = _parse(path)
        except (SyntaxError, UnicodeDecodeError):
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                used.add(node.id)
            elif isinstance(node, ast.Attribute):
                used.add(node.attr)

    return {n for n in twins if n not in used} - bound


@pytest.fixture(scope="session")
def uncalled_twins() -> set[str]:
    """Session-scoped fixture: the set of exported torch twins with no in-tree caller.

    Computed once per test session. The expensive AST walk over the repo
    happens here, not in the test itself.
    """
    return _compute_uncalled_twins()
