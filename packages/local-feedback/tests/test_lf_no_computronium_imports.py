"""G-RELEASE-1: local-feedback must not import computronium; demo regression."""

from __future__ import annotations

import ast
import importlib.util
import io
import sys
from contextlib import redirect_stdout
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
DEMO = Path(__file__).resolve().parents[1] / "examples" / "local_feedback_demo.py"


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
    spec = importlib.util.spec_from_file_location("local_feedback_demo", DEMO)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_demo_quick_passes() -> None:
    argv = sys.argv
    sys.argv = ["demo"]
    try:
        buf = io.StringIO()
        with redirect_stdout(buf):
            assert _load_demo().main() == 0
        assert "adaptive_late_ipn_greater_than_fixed: True" in buf.getvalue()
    finally:
        sys.argv = argv


def test_demo_deterministic_under_seed() -> None:
    argv = sys.argv
    sys.argv = ["demo", "--seed", "3"]
    try:
        buf1, buf2 = io.StringIO(), io.StringIO()
        with redirect_stdout(buf1):
            _load_demo().main()
        with redirect_stdout(buf2):
            _load_demo().main()
        out1 = "\n".join(
            line
            for line in buf1.getvalue().splitlines()
            if not line.startswith("walltime:")
        )
        out2 = "\n".join(
            line
            for line in buf2.getvalue().splitlines()
            if not line.startswith("walltime:")
        )
        assert out1 == out2
    finally:
        sys.argv = argv
