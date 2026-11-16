"""Locks for the memory decomposition and the binding gate (TODO93 §4, §9.5–6).

Three claims need a lock before a memory frontier can be reported. The
decomposition must sum to the peek (a fabricated term breaks the sum). The
activation term must scale with depth on a *measured* coefficient, not a
hardcoded one. And the gate must reject a cell whose regime is not
memory-bound, because a memory verdict from such a cell is vacuous.

Measured on the declared claim geometry -- Linear+ReLU, no norm, fp32, NVIDIA
L40S-class card: ``activations_mb ≈ c·L·B·W·4`` with **c ≈ 4.1**, not 1. The
repository's pre-TODO93 arithmetic assumed c≈1 (stored inputs only); the peak
also carries the backward gradient buffers at each layer, so the coefficient is
~4. The gate conclusion does not change (the share stays above 50%); the peak
estimate does, and the pilot appendix has to use the measured coefficient.
"""

from __future__ import annotations

import pytest
import torch

from computronium.core.rules import rule_system
from computronium.core.system_trainer import SystemTrainer, SystemTrainerConfig
from computronium.core.system_trainer._resources import (
    BINDING_SHARE,
    EpochResource,
    binding_verdict,
)

pytestmark = pytest.mark.skipif(
    not torch.cuda.is_available(), reason="peak memory is a CUDA measurement"
)

_WIDTH = 256
_CLASSES = 10
_BATCH = 2048


class _Batches:
    """A fixed, re-iterable batch list."""

    def __init__(self, batch: int = _BATCH, dim: int = _WIDTH, out: int = _CLASSES):
        self._pairs = [(torch.randn(batch, dim), torch.randint(0, out, (batch,)))]

    def __iter__(self):
        return iter(self._pairs)

    def __len__(self) -> int:
        return len(self._pairs)


def _epoch(depth: int, batch: int = _BATCH) -> EpochResource:
    """One training epoch of a plain backprop MLP at ``depth`` linear layers."""
    system = rule_system(
        "backprop",
        _WIDTH,
        _CLASSES,
        hidden_dims=(_WIDTH,) * (depth - 1),
        device="cuda",
    )
    trainer = SystemTrainer(
        system=system,
        config=SystemTrainerConfig(
            max_epochs=1, device="cuda", track_memory=True, track_flops=True
        ),
        train_data=_Batches(batch=batch),
    )
    trainer.train_epoch()
    return trainer.epoch_resources[-1]


def _coefficient(
    depth: int, delta_depth: int, delta_act_mb: float, batch: int
) -> float:
    """``c`` implied by an activation increase over ``delta_depth`` layers."""
    analytic_mb = delta_depth * batch * _WIDTH * 4 / 1024**2
    return delta_act_mb / analytic_mb


def test_peak_memory_is_monotone_in_depth() -> None:
    peaks = [_epoch(depth).peak_memory_mb for depth in (4, 8, 16)]
    first, second, third = peaks
    assert first is not None and second is not None and third is not None
    assert first < second < third, peaks


def test_activation_growth_carries_one_measured_coefficient() -> None:
    """Two independent depth deltas must imply the same ``c`` within 10 %.

    The cuBLAS workspace adds a batch-independent floor to every reading, so
    the coefficient is estimated from depth *differences*: the floor cancels,
    which is what makes this a calibration rather than a coincidence.
    """
    acts = [_epoch(depth).activations_mb for depth in (4, 8, 16)]
    shallow_mb, middle_mb, deep_mb = acts
    assert shallow_mb is not None and middle_mb is not None and deep_mb is not None
    shallow = _coefficient(4, 4, middle_mb - shallow_mb, _BATCH)
    deep = _coefficient(8, 8, deep_mb - middle_mb, _BATCH)

    spread = abs(shallow - deep) / deep
    assert spread < 0.10, f"c drifted {shallow:.2f} -> {deep:.2f} over depth"
    assert 2.0 < deep < 8.0, f"measured c={deep:.2f} is outside the linear-stack band"


def test_the_decomposition_sums_to_the_peak() -> None:
    """A fabricated term breaks the sum, which is the point of decomposing."""
    cost = _epoch(8)
    assert cost.optimizer_mb is not None and cost.optimizer_mb > 0.0, (
        "a stateful update must report its state"
    )
    assert cost.cpu_rss_mb is not None and cost.cpu_rss_mb > 0.0
    total = (
        float(cost.params_mb or 0.0)
        + float(cost.optimizer_mb)
        + float(cost.auxiliary_mb or 0.0)
        + float(cost.activations_mb or 0.0)
    )
    assert total == pytest.approx(cost.peak_memory_mb or 0.0, abs=1e-6)


def test_a_binding_cell_passes_the_gate() -> None:
    cost = _epoch(8)
    share = cost.activation_share
    assert share is not None and share >= BINDING_SHARE
    assert binding_verdict(cost) is True


def test_a_non_binding_cell_is_rejected() -> None:
    """The v2 failure mode: at W=512, B=1k, activations are a minority."""
    cost = EpochResource(
        epoch=0,
        epoch_time_s=1.0,
        steps=1,
        training_paths={},
        peak_memory_mb=100.0,
        params_mb=30.0,
        optimizer_mb=60.0,
        activations_mb=10.0,
    )
    assert binding_verdict(cost) is False


def test_an_unmeasured_share_is_not_a_pass() -> None:
    """``None`` is "no measurement", never a silent pass."""
    cost = EpochResource(epoch=0, epoch_time_s=1.0, steps=1, training_paths={})
    assert cost.activation_share is None
    assert binding_verdict(cost) is None
