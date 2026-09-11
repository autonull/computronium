"""T20.8.1: package boundaries — standalone packages never import computronium."""

from __future__ import annotations

import ast
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
STANDALONE = ("ceec-core", "psi-peft", "local-feedback")


def _py_files(pkg_root: Path) -> list[Path]:
    if not pkg_root.exists():
        return []
    return sorted(pkg_root.rglob("*.py"))


def test_standalone_packages_do_not_import_computronium() -> None:
    offenders: list[str] = []
    for pkg in STANDALONE:
        for path in _py_files(REPO / "packages" / pkg / "src"):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    names = [a.name for a in node.names]
                elif isinstance(node, ast.ImportFrom) and node.level == 0:
                    names = [node.module or ""]
                else:
                    continue
                offenders.extend(
                    f"{pkg}/{path.name}: {n}"
                    for n in names
                    if n.startswith("computronium")
                )
    assert not offenders, offenders


def test_standalone_packages_importable() -> None:
    missing = []
    for mod in ("ceec",):
        if mod not in sys.modules and not _importable(mod):
            missing.append(mod)
    assert not missing, f"install packages and re-run: {missing}"


def _importable(name: str) -> bool:
    import importlib.util

    return importlib.util.find_spec(name) is not None
