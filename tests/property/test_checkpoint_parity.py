"""Locks for the checkpointed backprop arm (TODO93 T4b, §4 acceptance ladder, §9.4).

Three claims need a lock before `backprop+checkpointing` can be the pilot's
baseline. (1) Checkpointed gradients are *exactly* plain gradients under
dropout -- checkpoint recomputation must preserve the RNG stream, and weights
must not be updated inside a retained segment. (2) The retained activation set
bends the depth curve: at the pilot point (L=64, W=1024, B=8192) the
checkpointed forward holds far fewer layer activations than plain. (3) The arm
fits the 8 GB card's 6.4 GiB budget at that point, which is its own acceptance
number (§4.1).

Measured on an RTX 3080 10 GiB (2026-11-15), W=1024, B=8192:
plain forward peak 2080 MB at L=64 vs 544 MB at L=16; checkpointed 480 MB at
L=64 vs 288 MB at L=16; checkpointed epoch peak 3894 MB at L=64 (budget 6554 MB).
The checkpointed epoch carries a param-sized gradient floor (~2.1 GB at L=64)
that checkpointing cannot remove; the activation term is what bends.

Every assertion here fails if its mechanism is removed: the parity lock breaks
without ``preserve_rng_state`` (the negative control runs the same fixture with
it disabled), and the curve lock breaks if the forward retains per-layer
activations.
"""

from __future__ import annotations

import pytest
import torch
from torch import nn

from computronium.core.gradient_checkpointing import (
    GradientCheckpointing,
    enable_gradient_checkpointing,
    segments_for_depth,
)
from computronium.core.presets import create_backprop_mlp
from computronium.core.system_trainer import (
    SystemTrainer,
    SystemTrainerConfig,
    compose_system,
)
from computronium.ontology import (
    CreditAssignmentConfig,
    DigitalSubstrate,
    EuclideanUpdate,
    FeedforwardGeometry,
    GeometryConfig,
    GradientCredit,
    InstantaneousDynamics,
    ParameterUpdateConfig,
    StateDynamicsConfig,
    SubstrateConfig,
)

_IN, _HIDDEN, _OUT = 16, 8, 4
_DROPOUT = 0.5


def _dropout_geometry(*, residual: bool = False) -> FeedforwardGeometry:
    """A Linear+ReLU stack with dropout, so RNG preservation is observable."""
    dims = (_IN, _HIDDEN, _HIDDEN, _OUT)
    layers: list[nn.Module] = []
    for i in range(len(dims) - 1):
        layers.append(nn.Linear(dims[i], dims[i + 1]))
        if i < len(dims) - 2:
            layers.append(nn.ReLU())
            layers.append(nn.Dropout(_DROPOUT))
    config = GeometryConfig.feedforward(
        input_dim=_IN,
        output_dim=_OUT,
        hidden_dims=(_HIDDEN, _HIDDEN),
        residual=residual,
    )
    return FeedforwardGeometry(config, layers=layers)


def _dropout_system(seed: int = 0, *, residual: bool = False):
    torch.manual_seed(seed)
    geometry = _dropout_geometry(residual=residual)
    return compose_system(
        DigitalSubstrate(
            SubstrateConfig(
                precision="float32",
                noise_level=0.0,
                weight_bounds=None,
                sparsity=0.0,
                device="cpu",
            )
        ),
        geometry,
        InstantaneousDynamics(StateDynamicsConfig.instantaneous()),
        GradientCredit(CreditAssignmentConfig.gradient()),
        EuclideanUpdate(ParameterUpdateConfig.euclidean(step_size=1e-2, momentum=0.0)),
    )


_BATCH, _SEED_STEP = 32, 7
# One fixed batch: an input drawn per call would differ between the two arms
# and the parity comparison would measure the data, not the checkpointing.
_X = torch.randn(_BATCH, _IN)
_Y = torch.randint(0, _OUT, (_BATCH,))


def _updated_weights(
    system, *, checkpointed: bool
) -> tuple[dict[str, torch.Tensor], dict[str, torch.Tensor]]:
    """One seeded train step: ``(initial, post-update)`` weights."""
    initial = {k: v.detach().clone() for k, v in system.geometry.params.items()}
    if checkpointed:
        enable_gradient_checkpointing(system)
    torch.manual_seed(_SEED_STEP)
    system.train_step(_X, _Y)
    updated = {k: v.detach().clone() for k, v in system.geometry.params.items()}
    return initial, updated


def test_segments_are_sqrt_of_linear_depth() -> None:
    assert segments_for_depth(1) == 1
    assert segments_for_depth(4) == 2
    assert segments_for_depth(16) == 4
    assert segments_for_depth(64) == 8
    assert segments_for_depth(100) == 10


def test_the_arm_declares_sqrt_segments_not_module_count() -> None:
    """A 64-layer MLP has 127 modules; √L counts Linears, not ReLUs."""
    system = create_backprop_mlp(8, (8,) * 63, 2)
    spec = enable_gradient_checkpointing(system)
    assert spec == GradientCheckpointing(segments=8)
    assert spec.to_identity() == {
        "grad_checkpointing_segments": 8,
        "compiled": False,
    }


def test_checkpointed_gradients_match_plain_under_dropout() -> None:
    """Preserved RNG and no in-segment update: parity is exact, not approximate."""
    system = _dropout_system()
    initial, plain = _updated_weights(system, checkpointed=False)
    system.geometry.update_params(initial)
    _, checkpointed = _updated_weights(system, checkpointed=True)
    for name, weight in plain.items():
        torch.testing.assert_close(checkpointed[name], weight, rtol=0, atol=0)
    assert any(
        (plain[name] - weight).abs().max() > 0 for name, weight in initial.items()
    ), "the step must actually move the weights"


def test_parity_fixture_fails_without_rng_preservation(monkeypatch) -> None:
    """Negative control: the lock's fixture must fail when its mechanism is off."""
    import computronium.ontology.geometry as geometry_module

    real_checkpoint = geometry_module.checkpoint

    def _unpreserved(function, *args, **kwargs):
        kwargs["preserve_rng_state"] = False
        return real_checkpoint(function, *args, **kwargs)

    system = _dropout_system()
    initial, plain = _updated_weights(system, checkpointed=False)
    system.geometry.update_params(initial)
    monkeypatch.setattr(geometry_module, "checkpoint", _unpreserved)
    _, unpreserved = _updated_weights(system, checkpointed=True)
    assert any(
        not torch.equal(unpreserved[name], weight) for name, weight in plain.items()
    ), "without RNG preservation the dropout masks drift and parity must break"


def test_residual_blocks_are_never_split() -> None:
    """A mid-block split would resume with the wrong skip tensor."""
    system = _dropout_system(residual=True)
    geometry = system.geometry
    geometry.train()
    x = torch.randn(_BATCH, _IN)
    with torch.enable_grad():
        torch.manual_seed(_SEED_STEP)
        plain_out = geometry.forward(x, system.substrate)
        enable_gradient_checkpointing(system)
        chunks = geometry._layer_chunks(geometry._checkpoint_segments)
        assert len(chunks) > 1 and all(
            isinstance(chunk[0], nn.Linear) for chunk in chunks
        )
        torch.manual_seed(_SEED_STEP)
        checkpointed_out = geometry.forward(x, system.substrate)
    torch.testing.assert_close(checkpointed_out, plain_out, rtol=1e-6, atol=1e-6)


pytestmark_gpu = pytest.mark.skipif(
    not torch.cuda.is_available(), reason="peak memory is a CUDA measurement"
)

_WIDTH, _CLASSES, _PILOT_BATCH = 1024, 10, 8192
# 8 GB card with the plan's 20 % headroom (TODO93 §4.1).
_PILOT_BUDGET_MB = 0.8 * 8 * 1024


class _Batches:
    """A fixed, re-iterable batch list."""

    def __init__(self) -> None:
        self._pairs = [
            (
                torch.randn(_PILOT_BATCH, _WIDTH),
                torch.randint(0, _CLASSES, (_PILOT_BATCH,)),
            )
        ]

    def __iter__(self):
        return iter(self._pairs)

    def __len__(self) -> int:
        return 1


def _forward_peak_mb(depth: int, *, checkpointed: bool) -> float:
    """Peak bytes a single grad-enabled forward holds at pilot width/batch."""
    system = create_backprop_mlp(
        _WIDTH,
        (_WIDTH,) * (depth - 1),
        _CLASSES,
        device="cuda",
        checkpoint_segments=segments_for_depth(depth) if checkpointed else None,
    )
    system.geometry.to("cuda")
    system.geometry.train()
    torch.cuda.empty_cache()
    torch.cuda.reset_peak_memory_stats()
    base = torch.cuda.memory_allocated()
    x = torch.randn(_PILOT_BATCH, _WIDTH, device="cuda")
    with torch.enable_grad():
        system.geometry.forward_with_intermediates(x, system.substrate)
    peak = (torch.cuda.max_memory_allocated() - base) / (1024 * 1024)
    del system, x
    torch.cuda.empty_cache()
    return peak


@pytestmark_gpu
def test_checkpointing_bends_the_forward_curve_down_in_depth() -> None:
    """The retained set is √L boundaries, so deep ckpt holds less than shallow plain."""
    plain_deep = _forward_peak_mb(64, checkpointed=False)
    ckpt_deep = _forward_peak_mb(64, checkpointed=True)
    plain_shallow = _forward_peak_mb(16, checkpointed=False)
    assert ckpt_deep < plain_deep * 0.5, (ckpt_deep, plain_deep)
    assert ckpt_deep < plain_shallow, (ckpt_deep, plain_shallow)


@pytestmark_gpu
def test_the_checkpointed_arm_fits_the_pilot_point() -> None:
    """L=64, W=1024, B=8192 on an 8 GB card -- T4b's own acceptance number."""
    system = create_backprop_mlp(
        _WIDTH,
        (_WIDTH,) * 63,
        _CLASSES,
        device="cuda",
        checkpoint_segments=8,
    )
    trainer = SystemTrainer(
        system=system,
        config=SystemTrainerConfig(
            max_epochs=1, device="cuda", track_memory=True, track_flops=True
        ),
        train_data=_Batches(),
    )
    trainer.train_epoch()
    resource = trainer.epoch_resources[-1]
    peak = resource.peak_memory_mb
    assert peak is not None and peak < _PILOT_BUDGET_MB, peak
    assert resource.activations_mb is not None and resource.activations_mb > 0.0
