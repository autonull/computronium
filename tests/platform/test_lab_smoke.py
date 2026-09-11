"""Platform smoke test — Lab quickstart and recipes demo run on CPU."""

from __future__ import annotations

import importlib.util
import io
import sys
from contextlib import redirect_stdout
from pathlib import Path

PKG = Path(__file__).resolve().parents[2] / "packages" / "computronium-lab"


def _run_example(name: str, argv: list[str]) -> str:
    path = PKG / "examples" / name
    spec = importlib.util.spec_from_file_location(name.removesuffix(".py"), path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    old_argv = sys.argv
    sys.argv = [name, *argv]
    try:
        buf = io.StringIO()
        with redirect_stdout(buf):
            assert module.main() == 0
        return buf.getvalue()
    finally:
        sys.argv = old_argv


def test_lab_quickstart_smoke(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    out = _run_example("lab_quickstart.py", [])
    assert "backprop_mlp" in out
    assert "report written" in out


def test_mechanism_recipes_demo_smoke() -> None:
    out = _run_example("mechanism_recipes_demo.py", [])
    assert "temporal_psi task_A" in out
    assert "adaptive_feedback" in out
    assert "role_split_muon_readout" in out
    assert "walltime" in out
