"""TODO98 P1 locks: one question per law, and the control that answers it.

A carrier law is decided by its step against its declared neutral companion;
a signal law by a fit whose cut-channel control must fail. These locks fail
when the wrong instrument decides a law, when a fit survives its control, and
when the batch reports a state it did not measure.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from computronium.primitives import cases, fit
from computronium.primitives.registry import get_primitive_spec
from computronium.primitives.surface import laws

pytestmark = pytest.mark.timeout(300)
ROOT = Path(__file__).resolve().parents[2]


def _law(suffix: str, axis: str) -> str:
    return next(
        law.id for law in laws() if law.axis == axis and law.id.endswith(f".{suffix}")
    )


def test_a_signal_law_fit_fails_without_its_mechanism() -> None:
    """A fit whose cut-channel control still fits is a test defect."""
    state, _ = fit.decide(law_kind="signal", invariant=True, fits=True, control=True)
    assert state == "test defect"
    state, _ = fit.decide(law_kind="signal", invariant=True, fits=True, control=False)
    assert state == "works"


def test_a_signal_law_fit_passes_under_some_legal_setting() -> None:
    """A law with a passing grid point is never called a defect."""
    spec = get_primitive_spec(_law("gradient", "credit"))
    assert spec is not None
    assert fit.kind(spec) == "signal"
    declared = fit.coordinate(spec)
    composed = fit.cell(spec, declared)
    measured = fit.measure(
        composed.system, fit.problem(composed.system, composed), steps=60
    )
    assert measured.reached, (measured.loss, measured.final)
    state, _ = fit.decide(
        law_kind="signal", invariant=True, fits=measured.reached, control=False
    )
    assert state == "works"
    state, _ = fit.decide(law_kind="signal", invariant=True, fits=False)
    assert state == "defect-or-gap (mechanism)"


def test_a_carrier_law_is_tested_by_its_digest() -> None:
    """A carrier law is decided by its companion digest, and a fit that runs
    without one is not a verdict."""
    state, reason = fit.decide(law_kind="carrier", invariant=True)
    assert state == "defect-or-gap (mechanism)"
    assert "digest" in reason
    differs = fit.Removal(digest="law", companion="companion")
    assert fit.decide(law_kind="carrier", invariant=True, removal=differs)[0] == "works"
    equal = fit.Removal(digest="law", companion="law")
    state, reason = fit.decide(law_kind="carrier", invariant=True, removal=equal)
    assert state == "inert"
    assert "companion" in reason
    silent = fit.Removal(digest="law", companion="law", silent=True)
    assert (
        fit.decide(law_kind="carrier", invariant=True, removal=silent)[0]
        == "defect-or-gap (mechanism)"
    )


def test_the_digest_separates_a_law_from_its_companion() -> None:
    """A quantizing substrate digests differently from ``digital``; the
    neutral law itself digests equal, so the reading is not always differ."""
    from computronium.primitives.registry import get_primitive_spec

    ternary = get_primitive_spec(_law("ternary", "substrate"))
    feedforward = get_primitive_spec(_law("feedforward", "geometry"))
    assert ternary is not None and feedforward is not None
    assert fit.bound(ternary, fit.coordinate(ternary)).differs
    assert not fit.bound(feedforward, fit.coordinate(feedforward)).differs


def test_a_signal_law_is_tested_by_its_fit() -> None:
    """A signal law is decided by the fit and its control, not a digest."""
    removal = fit.Removal(digest="law", companion="companion")
    state, _ = fit.decide(
        law_kind="signal",
        invariant=True,
        removal=removal,
        fits=True,
        control=False,
    )
    assert state == "works"
    state, _ = fit.decide(law_kind="signal", invariant=True, fits=True, control=True)
    assert state == "test defect"


def test_a_plastic_laws_modulation_reaches_the_digest() -> None:
    """The primitive step runs step then modulate, as the trainer does: a law
    whose declared channel is the modulation is measured, not only its ψ."""
    spec = get_primitive_spec(_law("routing", "plasticity"))
    assert spec is not None
    result = cases.step(spec, cases.build_case(spec, "", {}))
    assert result.activations


@pytest.mark.xfail(
    reason="gaps.GAPS['primitive.plasticity.substrate_coupled']: the P-axis "
    "carries no σ, so ψ ≡ σ has nothing to evolve",
    strict=True,
)
def test_the_plastic_step_carries_the_substrate_state() -> None:
    """The gap's trigger: the standard step must give ψ ≡ σ a substrate state."""
    from types import SimpleNamespace
    from typing import cast

    import torch

    from computronium.core.pipeline import _step_psi
    from computronium.ontology import CreditAssignment, Phase, SystemState

    class _Reader:
        psi_phase: str | None = None

        def __init__(self) -> None:
            self.sigma: dict = {}

        def step(self, psi: dict, z: Any, context: object) -> dict:
            self.sigma = dict(z.substrate)
            return psi

        def modulate(self, activations: Any, psi: dict) -> Any:
            return activations

    x = torch.randn(4, 8)
    y = torch.zeros(4, dtype=torch.long)
    settled = SystemState(x=x, y=y)
    settled.activations = [x, torch.randn(4, 16), torch.randn(4, 4)]
    reader = _Reader()
    _step_psi(
        reader,
        {},
        settled,
        x,
        y,
        Phase.FREE,
        cast("CreditAssignment", SimpleNamespace(phases=(Phase.FREE,))),
        object(),
    )
    assert reader.sigma


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


def test_the_batch_reports_a_missing_law(tmp_path: Path) -> None:
    """A selected law with no row is partial (exit 3), never a verdict."""
    from scripts.probes import p1_law_surface as batch

    options = batch.Options(axes=("credit",), steps=3, out=tmp_path)
    report = batch.Report(options=options)
    selected = list(laws())[:2]
    assert batch._exit(report, selected) == 3
