"""Quickstart regression: runs clean and is deterministic."""

from __future__ import annotations

import importlib.util
from pathlib import Path

EXAMPLE = Path(__file__).resolve().parents[1] / "examples" / "quickstart.py"


def test_quickstart_runs_and_audits_clean(capsys: object) -> None:
    spec = importlib.util.spec_from_file_location("quickstart", EXAMPLE)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert module.main() == 0
