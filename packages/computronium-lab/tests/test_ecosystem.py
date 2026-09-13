"""TODO23 Phase 5 — ecosystem adapters: callbacks + quick-tier benchmark."""

from __future__ import annotations

import json
from importlib.util import find_spec
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from pathlib import Path
from computronium_lab import (
    HuggingFaceCallback,
    LightningStabilityCallback,
    run_benchmark,
)
from computronium_lab.ecosystem import report_json


def test_lightning_callback_lazy_import_raises() -> None:
    if find_spec("lightning") is not None:
        pytest.skip("lightning installed; lazy-import path untestable")
    with pytest.raises(RuntimeError, match="requires lightning"):
        LightningStabilityCallback()


def test_hf_callback_records_history():
    cb = HuggingFaceCallback()
    cb.on_train_begin(None, None, None)
    cb.on_epoch_end(None, {"epoch": 1}, None, logs={"loss": 0.5})
    cb.on_epoch_end(None, {"epoch": 2}, None, logs={"loss": 0.25})
    assert [h["loss"] for h in cb.history] == [0.5, 0.25]


def test_hf_callback_evidence_dump(tmp_path: Path):
    path = tmp_path / "evidence.json"
    cb = HuggingFaceCallback(evidence_path=str(path))
    cb.on_train_begin(None, None, None)
    cb.on_epoch_end(None, {"epoch": 1}, None, logs={"loss": 1.0})
    cb.on_train_end(None, None, None)
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["epochs"] == 1
    assert payload["history"][0]["loss"] == 1.0


def test_run_benchmark_measured_rows():
    report = run_benchmark(["backprop_mlp", "ff_mlp"], epochs=1)
    assert len(report.rows) == 2
    assert all(r.accuracy >= 0.0 for r in report.rows)
    assert set(report.frontier) <= {r.preset for r in report.rows}
    assert report.walltime_s > 0


def test_report_json_roundtrip(tmp_path: Path):
    report = run_benchmark(["backprop_mlp"], epochs=1)
    path = tmp_path / "bench.json"
    payload = json.loads(report_json(report, str(path)))
    assert payload["frontier"] == ["backprop_mlp"]
    assert payload["rows"][0]["preset"] == "backprop_mlp"
