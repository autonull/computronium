"""G-RELEASE-1: psi-peft must not import computronium; demo quick regression."""

from __future__ import annotations

import ast
import importlib.util
import io
import sys
from contextlib import redirect_stdout
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
DEMO = Path(__file__).resolve().parents[1] / "examples" / "task_switching_demo.py"


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


def _load_demo():
    spec = importlib.util.spec_from_file_location("task_switching_demo", DEMO)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_demo_quick_passes() -> None:
    argv = sys.argv
    sys.argv = ["demo"]
    try:
        assert _load_demo().main() == 0
    finally:
        sys.argv = argv


def test_demo_deterministic_under_seed() -> None:
    module = _load_demo()
    argv = sys.argv
    sys.argv = ["demo", "--seed", "7"]
    try:
        filtered = []
        for _run in range(2):
            buf = io.StringIO()
            with redirect_stdout(buf):
                module.main()
            filtered.append([
                ln for ln in buf.getvalue().splitlines() if "adapt=" not in ln
            ])
    finally:
        sys.argv = argv
    assert filtered[0] == filtered[1]
