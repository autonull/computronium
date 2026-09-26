"""One meaning for "the triton rung is available here, now" (TODO36 §4.2).

The point of these tests is that an *unlaunchable* kernel reports unavailable.
Before this module existed, `HAS_TRITON_PC` and its four siblings were `True` on
this box while 12 of the 17 kernels they guarded could not compile — the flags
answered "is triton importable", and every caller read them as "will this run".

§4.5 then wrote a specification for each of those 12 and all 17 now compile, so
the demonstration this file used to give from the real tree — a family with a
broken kernel reporting unavailable — is no longer available *by accident*. It is
now injected instead: :func:`test_a_family_whose_kernel_does_not_compile_reports_unavailable`
marks one family broken and reads the flag, which is a stronger test than the old
one because it cannot rot into a tautology.
"""

import pytest
import torch

from computronium.acceleration import availability
from computronium.acceleration.availability import (
    CompileState,
    KernelReport,
    compile_report,
    fixtures,
    regressions,
    triton_rung_available,
    triton_stack_available,
    unfixtured_kernels,
)
from computronium.acceleration.backends import TRITON_IMPORTED, kernel_available

requires_triton = pytest.mark.skipif(
    not TRITON_IMPORTED, reason="triton is not installed"
)
requires_cuda = pytest.mark.skipif(
    not torch.cuda.is_available(), reason="no CUDA device to compile on"
)

#: Discovered kernels with no compile fixture, each with the test that compiles it
#: by running it. Adding a module-level ``@triton.jit`` means adding a row here or
#: a fixture above — the census cannot be widened by accident.
GPU_TESTED = frozenset({
    "complex_substrate._complex_matmul_kernel",
    # A device helper, not a launchable kernel: compiled by
    # tests/acceleration/test_snn_stdp_spec.py through both STDP kernels.
    "snn_kernels._stdp_phase_delta",
    "tile_kernels._tile_activity_update_kernel",
    "tile_kernels._tile_contrastive_update_kernel",
    "tile_kernels._tile_hebbian_update_kernel",
    "tile_kernels._tile_learned_routing_kernel",
    "tile_kernels._tile_prediction_kernel",
    "tile_kernels._tile_random_routing_kernel",
    "tile_kernels._tile_topk_routing_kernel",
})


def test_kernel_available_triton_is_measured_not_inferred(monkeypatch) -> None:
    """`kernel_available("triton")` is a compilation, not a CUDA check."""
    monkeypatch.setattr(torch.cuda, "is_available", lambda: True)
    monkeypatch.setattr(availability, "_triton", lambda: None)
    assert kernel_available("triton") is False
    assert triton_stack_available() is False


def test_kernel_available_cupy_is_not_assumed() -> None:
    """`kernel_available("cupy")` used to return True from an empty try block."""
    from computronium.acceleration.backends import HAS_CUPY

    assert kernel_available("cupy") is HAS_CUPY


def test_unknown_technology_is_unavailable() -> None:
    assert kernel_available("quantum") is False


@requires_triton
@requires_cuda
def test_every_family_reports_available_when_every_kernel_compiles() -> None:
    """The measured state of the tree: every family with a fixture is available.

    This is the sentence §4.5's specifications changed. It was ``snn`` that used
    to be ``False`` here, with two STDP kernels that could not compile.
    """
    assert TRITON_IMPORTED, "the premise of this test is that triton is importable"
    assert triton_stack_available() is True
    unfixtured = {
        r.family for r in compile_report() if r.state is not CompileState.COMPILES
    }
    assert unfixtured == set()
    for family in ("snn", "fa", "pcalm", "pc", "hebbian", "pepita", "ff"):
        assert triton_rung_available(family) is True


@requires_triton
@requires_cuda
def test_a_family_whose_kernel_does_not_compile_reports_unavailable(
    monkeypatch,
) -> None:
    """§4.2's done-when: a flag is ``False`` for a kernel that does not compile.

    Injected rather than found, so the property holds whatever the tree's kernels
    do next. A family is unavailable when *any* of its kernels fails, which is
    the whole claim: a half-working family is a family that will not run.
    """
    snn = next(f for f in fixtures() if f.family == "snn")
    monkeypatch.setitem(
        availability._STATE_CACHE,  # ruff: ignore[private-member-access]  (the cache is the measurement)
        snn.name,
        KernelReport(snn.name, "snn", CompileState.FAILS, "injected"),
    )
    assert triton_rung_available("snn") is False
    assert triton_rung_available("fa") is True


@requires_cuda
def test_no_triton_means_no_rung(monkeypatch) -> None:
    monkeypatch.setattr(torch.cuda, "is_available", lambda: False)
    assert triton_rung_available("fa") is False
    assert triton_stack_available() is False


def test_every_fixture_name_is_unique() -> None:
    names = [fixture.name for fixture in fixtures()]
    assert len(names) == len(set(names))


def test_fixture_names_match_their_modules() -> None:
    for fixture in fixtures():
        assert fixture.name == f"{fixture.module.rsplit('.', 1)[-1]}.{fixture.attr}"


@requires_triton
def test_census_is_closed() -> None:
    """No module-level triton kernel escapes the fixture table or the allowlist."""
    assert set(unfixtured_kernels()) == GPU_TESTED


@requires_triton
@requires_cuda
def test_report_covers_every_fixture_exactly_once() -> None:
    assert [r.name for r in compile_report()] == [f.name for f in fixtures()]


@requires_cuda
def test_baseline_has_an_entry_for_every_fixture() -> None:
    baseline = availability._baseline()  # ruff: ignore[private-member-access]  (the recorded state is the point)
    assert set(baseline) == {fixture.name for fixture in fixtures()}
    assert set(baseline.values()) <= {state.value for state in CompileState}


@requires_cuda
def test_no_regression_from_the_recorded_baseline() -> None:
    assert regressions() == ()


@requires_cuda
def test_cli_check_passes() -> None:
    assert availability.main(["--check"]) == 0


def test_cli_rejects_nothing_and_parses() -> None:
    assert availability.main([]) == 0
