"""Locks for the memory-frontier pilot (TODO93 T6, §4, §9.7-8).

The pilot has three jobs, and each one is a lock here.

**The arithmetic.** At the registered operating point the measured activation
coefficient must be the declared one (``c = 4.1``), otherwise every registered
budget is fiction. Two depth deltas at the pilot width and batch decide it in
one measurement.

**The gate.** The plain-backprop arm's activation share must clear 50 % at the
point, or the cell is ``[regime-mismatch]`` and no memory claim can rest on it.

**The mechanism.** A frontier claim needs the treatment arm's activation set
below the checkpointed baseline's. ``backprop+ckpt`` passes that lock today
(measured 0.39x). The hybrid passes it because it owns its free pass: the
pipeline keeps one readout activation instead of the store-all forward the
hybrid's head and trunk recompute anyway (TODO93 T6b, measured 210 MB against
the checkpointed arm's 437 MB at L=32/B=4096/W=512). The tripwire lock keeps
the capability load-bearing: with the owned pass removed, the pipeline's
``forward_pass`` runs again and the hook records it.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
import torch

from computronium.core import pipeline
from computronium.core.system_trainer._resources import BINDING_SHARE
from computronium.validation import memory_frontier as frontier

if TYPE_CHECKING:
    from collections.abc import Iterator

_GPU = pytest.mark.skipif(
    not torch.cuda.is_available(), reason="the decomposition needs a CUDA peak"
)
#: The claim point is L=32/B=8192/W=1024 (~4.5 GB); the locks run the same
#: geometry at W=512/B=4096 so four xdist workers can hold it at once. The
#: coefficient and the composed-path ratio are width/batch-invariant, which is
#: what makes the smaller point a lock rather than a second measurement.
_POINT = frontier.PilotPoint(width=512, batch=4096, steps=4)
_SIGMA = 0.10


@pytest.fixture(scope="module")
def cifar() -> Iterator[tuple[torch.Tensor, ...]]:
    yield frontier._cifar()


def _cell(arm: str, depth: int = _POINT.depth, cifar=None) -> frontier.ArmCell:
    x_train, y_train, x_test, y_test = cifar or frontier._cifar()
    point = _POINT.scaled(depth=depth)
    return frontier._measure(
        arm,
        point,
        lr=frontier.FROZEN_LR[arm],
        seed=frontier.PILOT_SEEDS[0],
        device="cuda",
        x_train=x_train,
        y_train=y_train,
        x_test=x_test,
        y_test=y_test,
    )


@_GPU
def test_the_measured_coefficient_is_the_declared_one(cifar) -> None:
    cells = [_cell("backprop", depth=depth, cifar=cifar) for depth in (8, _POINT.depth)]
    shallow, deep = cells
    assert shallow.activations_mb is not None and deep.activations_mb is not None
    analytic = frontier._layers_mb(_POINT, _POINT.depth) - frontier._layers_mb(
        _POINT, 8
    )
    measured = (deep.activations_mb - shallow.activations_mb) / analytic
    assert measured == pytest.approx(frontier.DECLARED_C, rel=_SIGMA), (
        f"measured c={measured:.2f} at the registered point"
    )


@_GPU
def test_the_plain_arm_binds_the_regime(cifar) -> None:
    """The gate reads the unrecovered arm; a non-binding cell is not evidence."""
    cell = _cell("backprop", cifar=cifar)
    assert cell.activation_share is not None
    assert cell.activation_share >= BINDING_SHARE, cell
    assert cell.binding is True


@_GPU
def test_checkpointing_halves_the_activation_set_on_the_composed_path(cifar) -> None:
    plain = _cell("backprop", cifar=cifar)
    checkpointed = _cell("backprop+ckpt", cifar=cifar)
    assert plain.activations_mb and checkpointed.activations_mb
    assert checkpointed.activations_mb <= 0.5 * plain.activations_mb, (
        f"ckpt {checkpointed.activations_mb:.0f} MB vs plain {plain.activations_mb:.0f} MB"
    )


@_GPU
def test_the_hybrid_activation_set_is_half_the_checkpointed_arms(cifar) -> None:
    hybrid = _cell("hybrid", cifar=cifar)
    checkpointed = _cell("backprop+ckpt", cifar=cifar)
    assert hybrid.activations_mb and checkpointed.activations_mb
    assert hybrid.activations_mb <= 0.5 * checkpointed.activations_mb, (
        f"hybrid {hybrid.activations_mb:.0f} MB vs ckpt {checkpointed.activations_mb:.0f} MB"
    )


def _step_calls(monkeypatch, arm: str) -> list[int]:
    """One train step with the pipeline's store-all forward counted."""
    calls: list[int] = []
    original = pipeline.forward_pass

    def spy(*args, **kwargs):
        calls.append(1)
        return original(*args, **kwargs)

    monkeypatch.setattr(pipeline, "forward_pass", spy)
    point = frontier.PilotPoint(depth=4, width=16, batch=8, steps=2)
    system = frontier.build_arm(arm, point, lr=0.1, seed=1)
    x = torch.randn(8, point.input_dim)
    y = torch.randint(0, point.classes, (8,))
    system.train_step(x, y)
    return calls


def test_the_hybrid_owns_its_free_pass(monkeypatch) -> None:
    """The tripwire: a pipeline forward for the hybrid means the pass is lost."""
    assert not _step_calls(monkeypatch, "hybrid")


def test_the_plain_arm_reads_the_pipeline_forward(monkeypatch) -> None:
    """Positive control: the tripwire above is load-bearing, not dead."""
    assert _step_calls(monkeypatch, "backprop")


def test_the_arms_are_wired_to_their_declared_credits() -> None:
    point = frontier.PilotPoint(depth=4, width=16, batch=8, steps=4)

    def build(arm: str):
        return frontier.build_arm(arm, point, lr=0.1, seed=1)

    assert build("backprop").credit.IDENTITY_CARD.estimator_kind == "exact"
    assert build("backprop+ckpt").geometry._checkpoint_segments == 2
    assert build("hybrid").credit.IDENTITY_CARD.estimator_kind == "hybrid"
    assert build("local").credit.IDENTITY_CARD.estimator_kind == "objective_local"
    with pytest.raises(ValueError, match="unknown arm"):
        build("consolidation")


def test_the_arithmetic_admits_the_pilot_point_and_refuses_depth_64() -> None:
    point = frontier.PilotPoint()
    assert point.affordable()
    assert point.peak_mb() == pytest.approx(
        frontier.DECLARED_C * 32 * 8192 * 1024 * 4 / 2**20 + 2 * point.params_mb()
    )
    assert not frontier.PilotPoint(depth=64).affordable()
    assert frontier.ADMISSION_BUDGET_MB == 0.8 * 8192


def test_the_activation_arithmetic_is_linear_in_depth() -> None:
    point = frontier.PilotPoint()
    shallow = point.activation_mb(depth=8)
    assert point.activation_mb() == pytest.approx(4 * shallow)
    assert point.activation_mb(depth=16) == pytest.approx(2 * shallow)
    assert point.activation_mb(depth=32) == pytest.approx(
        frontier.DECLARED_C * frontier._layers_mb(point, 32)
    )


@_GPU
def test_the_pilot_runner_writes_its_appendix(tmp_path) -> None:
    """The cell loop, both controls, and the writer, at a throwaway point.

    The controls are *reported* here, not asserted: at width 32 the cuBLAS floor
    dominates the depth delta, which is exactly why the registered point is
    priced at W=1024/B=8192 (see the pilot appendix in `docs/BENCHMARKS.md`).
    """
    point = frontier.PilotPoint(depth=4, width=32, batch=64, steps=4)
    report = frontier.run_pilot(point, seeds=(1,), device="cuda", output_dir=tmp_path)

    assert {row.arm for row in report.arms} == set(frontier.ARMS)
    assert all(cell.steps == point.steps for cell in report.cells)
    assert report.learning.depth == 8
    written = (tmp_path / "results.json").read_text(encoding="utf-8")
    assert '"controls_passed"' in written
    assert (tmp_path / "appendix.md").exists()


def _rung_cell(
    depth: int,
    *,
    val_acc: float,
    stream_norm: bool = False,
    lr: float = 0.03,
    factor: float = 1.0,
) -> frontier.DepthCell:
    return frontier.DepthCell(
        depth=depth,
        stream_norm=stream_norm,
        lr=lr,
        seed=1,
        val_acc=val_acc,
        activations_mb=factor * 100.0 * depth,
    )


def test_the_depth_rung_verdict_reads_the_floor_and_the_confirmation() -> None:
    """The depth rung's decision: plateau, lift, floor, and the second seed.

    The gate is the shallow arm's floor, not a fresh number: a best point at
    the floor boundary plus a confirmation seed below it must refuse.
    """
    floor = 0.375
    plain = (_rung_cell(8, val_acc=0.39), _rung_cell(32, val_acc=0.10))
    ladder = (
        _rung_cell(32, val_acc=0.30, stream_norm=True, lr=1e-3, factor=1.45),
        _rung_cell(32, val_acc=0.31, stream_norm=True, lr=1e-2, factor=1.45),
    )
    shallow = _rung_cell(8, val_acc=0.38, stream_norm=True)
    lifted = frontier.DepthRung(
        floor=floor,
        plain=plain,
        normalized_shallow=shallow,
        normalized=ladder,
        confirmation=_rung_cell(32, val_acc=0.37, stream_norm=True),
    )
    assert lifted.plateaued
    assert lifted.left_the_plateau
    assert not lifted.reaches_floor
    assert lifted.best.val_acc == 0.31
    assert lifted.activation_ratio == pytest.approx(1.45)

    met = frontier.DepthRung(
        floor=floor,
        plain=plain,
        normalized_shallow=shallow,
        normalized=(*ladder, _rung_cell(32, val_acc=0.38, stream_norm=True, lr=3e-2)),
        confirmation=_rung_cell(32, val_acc=0.385, stream_norm=True),
    )
    assert met.reaches_floor

    no_plateau = frontier.DepthRung(
        floor=floor,
        plain=(plain[0], _rung_cell(32, val_acc=0.38)),
        normalized_shallow=shallow,
        normalized=ladder,
        confirmation=_rung_cell(32, val_acc=0.39, stream_norm=True),
    )
    assert not no_plateau.plateaued


def test_the_rung_point_carries_its_pass_into_the_geometry() -> None:
    """The rung's coordinate is the point's pass, not a dropped argument."""
    plain = frontier.build_arm(
        "backprop",
        frontier.PilotPoint(depth=4, width=8, batch=8, steps=2),
        lr=0.1,
        seed=1,
    )
    normalized = frontier.build_arm(
        "backprop",
        frontier.PilotPoint(depth=4, width=8, batch=8, steps=2, stream_norm=True),
        lr=0.1,
        seed=1,
    )
    assert plain.geometry.config.stream_norm is False
    assert normalized.geometry.config.stream_norm is True
    assert frontier.PilotPoint(stream_norm=True).scaled(depth=4).stream_norm is True
