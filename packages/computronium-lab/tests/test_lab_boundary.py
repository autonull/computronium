"""T21.3A.7 lab boundary: computronium-lab is the sanctioned integration layer.

Direction: lab MAY import computronium (that is its job — preset factories
over the ontology); computronium and the standalone packages must NOT
import computronium_lab. Decision recorded in PLATFORM_LAUNCH.md.
"""

from __future__ import annotations

import ast
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]


def _imported_root_modules(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    names: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.extend(a.name.split(".")[0] for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            names.append(node.module.split(".")[0])
    return names


def test_lab_may_import_computronium() -> None:
    src = Path(__file__).resolve().parents[1] / "src"
    assert any(
        "computronium" in _imported_root_modules(p) for p in src.rglob("*.py")
    ), "lab must integrate computronium (sanctioned direction)"


def test_nothing_imports_the_lab() -> None:
    offenders: list[str] = []
    targets = [REPO_ROOT / "computronium"] + [
        d / "src"
        for d in (REPO_ROOT / "packages").iterdir()
        if d.name != "computronium-lab"
    ]
    for base in targets:
        if not base.exists():
            continue
        for path in base.rglob("*.py"):
            if "computronium_lab" in _imported_root_modules(path):
                offenders.append(str(path.relative_to(REPO_ROOT)))
    assert not offenders, f"forbidden computronium_lab imports: {offenders}"
