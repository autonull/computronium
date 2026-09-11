"""G-RELEASE-1: ceec-core must not import computronium."""

from __future__ import annotations

import ast
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"


def test_no_computronium_imports() -> None:
    offenders: list[str] = []
    for path in SRC.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names = [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom) and node.level == 0:
                names = [node.module or ""]
            else:
                continue
            offenders.extend(
                f"{path.name}:{n}" for n in names if n.startswith("computronium")
            )
    assert not offenders, f"computronium imports in standalone package: {offenders}"


def test_constraints_interface() -> None:
    from ceec import ConstraintResult

    class MinLength:
        def validate(self, candidate: dict[str, object]) -> ConstraintResult:
            ok = len(str(candidate.get("statement", ""))) >= 8
            return ConstraintResult(name="min_length", passed=ok)

    assert MinLength().validate({"statement": "short"}) is not None
    assert MinLength().validate({"statement": "long enough statement"}).passed
