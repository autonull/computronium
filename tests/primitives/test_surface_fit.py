"""TODO98 P1 locks: the fit, its control, and the batch's verdicts.

A fit that passes with its mechanism removed measures the optimizer, not the
law: these locks make that a test defect and never a result. The batch's
calibration gate, its restart, and its refusal to report an unproven axis
as ``works`` are locks too, so a green table cannot stand without them.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from computronium.primitives import fit
from computronium.primitives.registry import get_primitive_spec
from computronium.primitives.surface import laws

pytestmark = pytest.mark.timeout(300)
ROOT = Path(__file__).resolve().parents[2]


def _law(suffix: str, axis: str) -> str:
    return next(
        law.id for law in laws() if law.axis == axis and law.id.endswith(f".{suffix}")
    )


def test_a_law_fit_fails_without_its_mechanism() -> None:
    """A fit whose mechanism-removed control still fits is a test defect."""
    state, _ = fit.decide(invariant=True, fits=True, control=True, knob=True)
    assert state == "test defect"
    state, _ = fit.decide(invariant=True, fits=True, control=False, knob=True)
    assert state == "works"


def test_a_law_fit_passes_under_some_legal_setting() -> None:
    """A law with a passing grid point is never called a defect."""
    spec = get_primitive_spec(_law("gradient", "credit"))
    assert spec is not None
    declared = fit.coordinate(spec)
    composed = fit.cell(spec, declared)
    measured = fit.measure(
        composed.system, fit.problem(composed.system, composed), steps=60
    )
    assert measured.reached, (measured.loss, measured.final)
    state, _ = fit.decide(
        invariant=True, fits=measured.reached, control=False, knob=True
    )
    assert state == "works"
    state, _ = fit.decide(invariant=True, fits=False, control=False, knob=True)
    assert state == "defect-or-gap (mechanism)"


def test_an_inert_knob_is_a_declaration_defect() -> None:
    """A declared knob that moves no fit is a declaration defect, not tuning."""
    state, reason = fit.decide(invariant=True, fits=True, control=False, knob=False)
    assert state == "declaration defect"
    assert "inert" in reason
    assert fit.decide(invariant=True, fits=True, control=False, knob=True)[0] == "works"


def test_the_batch_refuses_a_verdict_without_a_control() -> None:
    """An axis with no demonstrated control is never reported as ``works``."""
    state, reason = fit.decide(invariant=True, fits=True, control=None, knob=True)
    assert state == "unproven control"
    assert "control" in reason
    state, _ = fit.decide(invariant=True, fits=False, control=None, knob=None)
    assert state == "defect-or-gap (mechanism)"


def test_the_batch_calibration_gate_exits_nonzero(tmp_path: Path) -> None:
    """A declared non-pass that fits writes no table and exits 1."""
    from scripts.probes import p1_law_surface as batch

    options = batch.Options(axes=("geometry",), steps=3, out=tmp_path)
    report = batch.Report(options=options)
    report.exit_code = 1
    report.calibration = {
        "primitive.geometry.conv": {"expected": "refused", "state": "works"}
    }
    batch._write(report)
    assert not (tmp_path / "surface.md").exists()
    assert "conv" in (tmp_path / "calibration.md").read_text()


def test_the_batch_is_restartable(tmp_path: Path) -> None:
    """A finished row does not re-run, and its record is the one already written."""
    from scripts.probes import p1_law_surface as batch

    options = batch.Options(axes=("credit",), steps=3, lanes=1, limit=1, out=tmp_path)
    first = batch._run(options)
    assert first.rows
    record = next(iter(first.rows.values()))
    second = batch._run(
        batch.Options(
            axes=options.axes,
            steps=options.steps,
            lanes=1,
            limit=1,
            out=tmp_path,
            resume=True,
        )
    )
    cached = next(row for row in second.rows.values() if row["id"] == record["id"])
    assert cached["seconds"] == record["seconds"]
    assert json.loads((tmp_path / "surface.json").read_text())["rows"]


def test_the_batch_marks_unproven_axes(tmp_path: Path) -> None:
    """An unproven axis is a partial wave (exit 3), never a verdict."""
    from scripts.probes import p1_law_surface as batch

    options = batch.Options(axes=("credit",), steps=3, out=tmp_path)
    report = batch.Report(options=options)
    report.rows["a"] = {"id": "primitive.credit_assignment.gradient", "state": "works"}
    report.rows["b"] = {
        "id": "primitive.credit_assignment.homeostatic",
        "state": "unproven control",
    }
    selected = list(laws())
    assert batch._exit(report, selected) == 3
