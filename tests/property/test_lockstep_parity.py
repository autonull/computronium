"""Locks for the lockstep two-pass rung (TODO93 T3, §8.1, §9.3).

Two claims need a lock before the memory frontier can run on a local-credit arm.

**Exactness.** ``train_step`` updates each layer as soon as that layer's two
passes exist instead of storing every activation and updating afterwards. The
reordering is exact *because each ``W_l`` is used once per pass before its own
update*: layer ``l+1`` reads ``W_{l+1}`` and activations computed before ``W_l``
moved. The locks below compare the per-layer deltas at ``atol=0`` against an
expression written from the equations, not against the code under test.

**Depth-flat peak.** The lockstep keeps one layer's two chains live; the
store-all rung keeps ``L`` layers' worth per chain. The memory lock measures the
CUDA peak at ``L=4/8/16/32`` and fails if it bends with depth. The negative
control materializes the contrast stream — the mechanism removal — and its peak
must grow with depth.

Measured on an RTX 3080 10 GiB (2026-11-16), Linear+ReLU fp32, W=512, B=4096,
L=4/8/16/32 — lockstep peak is flat at **66.3 MB** (FF) and **58.5 MB** (PEPITA);
the retained stream reaches 576.4 MB (FF) and 568.5 MB (PEPITA) at L=32
(docs/BENCHMARKS.md).
"""

from __future__ import annotations

from types import SimpleNamespace

import pytest
import torch

from computronium.acceleration import ff_kernels
from computronium.acceleration.ff_kernels import (
    FFKernelBackend,
    PEPITAKernelBackend,
    lockstep_contrasts,
)
from computronium.acceleration.kernel_backend import (
    AlgorithmFamily,
    HardwareTarget,
    KernelConfig,
)

_IN, _HIDDEN, _OUT, _BATCH = 6, 8, 4, 5


def _config(family: AlgorithmFamily, *, cuda: bool = False) -> KernelConfig:
    return KernelConfig(
        algorithm=family,
        hardware=HardwareTarget.CUDA if cuda else HardwareTarget.CPU,
        extra={"input_dim": _IN, "output_dim": _OUT, "feedback_matrix_scale": 0.5},
    )


def _batch_scale(pre: torch.Tensor, post: torch.Tensor) -> torch.Tensor:
    """``postᵀ·pre / B`` written from the definition, independent of the rung."""
    return (post.T @ pre) / pre.shape[0]


def _weight_delta(pre_a, post_a, pre_b, post_b) -> torch.Tensor:
    return _batch_scale(pre_a, post_a) - _batch_scale(pre_b, post_b)


def _snapshot(modules) -> list[torch.Tensor]:
    return [p.detach().clone() for module in modules for p in module.parameters()]


def _restore(modules, state: list[torch.Tensor]) -> None:
    for parameter, tensor in zip(
        (p for module in modules for p in module.parameters()), state, strict=True
    ):
        parameter.data.copy_(tensor)


def _ff_stack(seed: int = 0):
    """Seeded FF stack (label columns appended to the input) and a fixed batch."""
    torch.manual_seed(seed)
    layers = [
        torch.nn.Linear(_IN + _OUT, _HIDDEN),
        torch.nn.Linear(_HIDDEN, _HIDDEN),
        torch.nn.Linear(_HIDDEN, _OUT),
    ]
    backend = FFKernelBackend()
    backend.initialize(_config(AlgorithmFamily.FF))
    backend.set_model_ref(layers, torch.nn.ReLU())
    return backend, layers, torch.randn(_BATCH, _IN), torch.randint(0, _OUT, (_BATCH,))


def _ff_store_all(backend: FFKernelBackend, x: torch.Tensor, y: torch.Tensor) -> None:
    """The store-all rung: both activation lists retained, then one update sweep."""
    with torch.no_grad():
        _pos_out, pos_acts = backend.forward_positive(x, y)
        _neg_out, neg_acts = backend.forward_negative(x, y)
        backend.update_weights(backend.backward(pos_acts, neg_acts), 1.0)


def test_forward_forward_lockstep_is_the_store_all_schedule() -> None:
    backend, layers, x, y = _ff_stack()

    with torch.no_grad():
        chain_a, chain_b = backend._labelled_inputs(x, y)
        contrasts = list(lockstep_contrasts(layers, chain_a, chain_b, torch.nn.ReLU()))

    assert len(contrasts) == len(layers)
    pre_a, pre_b = chain_a, chain_b
    for contrast in contrasts:
        torch.testing.assert_close(
            contrast.weight,
            _weight_delta(pre_a, contrast.post_a, pre_b, contrast.post_b),
            rtol=0,
            atol=0,
        )
        torch.testing.assert_close(
            contrast.bias,
            contrast.post_a.mean(dim=0) - contrast.post_b.mean(dim=0),
            rtol=0,
            atol=0,
        )
        pre_a, pre_b = contrast.post_a, contrast.post_b
        assert contrast.weight.abs().max() > 0, "the contrast must move the layer"

    state = _snapshot(layers)
    _ff_store_all(backend, x, y)
    stored = _snapshot(layers)
    assert all(
        (weight - start).abs().max() > 0
        for weight, start in zip(stored, state, strict=True)
    ), "the reference rung must move the weights"

    _restore(layers, state)
    backend.train_step(x, y)
    for parameter, weight in zip(
        (p for layer in layers for p in layer.parameters()), stored, strict=True
    ):
        torch.testing.assert_close(parameter, weight, rtol=0, atol=1e-7)


def _pepita_stack(seed: int = 0):
    torch.manual_seed(seed)
    layers = [torch.nn.Linear(_IN, _HIDDEN), torch.nn.Linear(_HIDDEN, _OUT)]
    backend = PEPITAKernelBackend()
    backend.initialize(_config(AlgorithmFamily.PEPITA))
    backend.set_model_ref(layers, torch.nn.ReLU())
    return backend, layers, torch.randn(_BATCH, _IN), torch.randint(0, _OUT, (_BATCH,))


def _pepita_store_all(
    backend: PEPITAKernelBackend, x: torch.Tensor, y: torch.Tensor
) -> None:
    """The store-all rung: standard and modulated activation lists, then update."""
    with torch.no_grad():
        standard = backend._forward_last(x)
        target = torch.nn.functional.one_hot(y, _OUT).float()
        _std_out, std_acts = backend.forward_standard(x)
        _mod_out, mod_acts = backend.forward_error_modulated(x, target - standard)
        backend.update_weights(backend.backward(std_acts, mod_acts), 1.0)


def test_pepita_lockstep_recomputes_the_standard_chain_exactly() -> None:
    backend, layers, x, y = _pepita_stack()
    with torch.no_grad():
        standard = backend._forward_last(x)
        target = torch.nn.functional.one_hot(y, _OUT).float()
        modulated = backend._modulated_input(x, target - standard)
        contrasts = list(lockstep_contrasts(layers, x, modulated, torch.nn.ReLU()))

    pre_a, pre_b = x, modulated
    for contrast in contrasts:
        torch.testing.assert_close(
            contrast.weight,
            _weight_delta(pre_a, contrast.post_a, pre_b, contrast.post_b),
            rtol=0,
            atol=0,
        )
        pre_a, pre_b = contrast.post_a, contrast.post_b
    # Pass 2 recomputes the standard chain: it must equal pass 1's output.
    torch.testing.assert_close(contrasts[-1].post_a, standard, rtol=0, atol=0)

    state = _snapshot(layers)
    _pepita_store_all(backend, x, y)
    stored = _snapshot(layers)
    assert all(
        (weight - start).abs().max() > 0
        for weight, start in zip(stored, state, strict=True)
    ), "the reference rung must move the weights"

    _restore(layers, state)
    backend.train_step(x, y)
    for parameter, weight in zip(
        (p for layer in layers for p in layer.parameters()), stored, strict=True
    ):
        torch.testing.assert_close(parameter, weight, rtol=0, atol=1e-7)


def _bespoke_store_all(model: SimpleNamespace, scale: float, x, y) -> None:
    """The store-all schedule for the bespoke surface, from the equations."""
    layers, out_layer = list(model.layers), model.out_layer
    with torch.no_grad():
        acts, h = [], x
        for layer in layers:
            h = torch.nn.functional.relu(layer(h))
            acts.append(h)
        error = out_layer(h) - torch.nn.functional.one_hot(y, _OUT).float()
        modulated = x + error @ model.feedback_matrix.T * scale
        mod_acts, h = [], modulated
        for layer in layers:
            h = torch.nn.functional.relu(layer(h))
            mod_acts.append(h)
        for layer, std_post, mod_post, std_pre, mod_pre in zip(
            layers,
            acts,
            mod_acts,
            [x, *acts[:-1]],
            [modulated, *mod_acts[:-1]],
            strict=True,
        ):
            layer.weight.add_(
                -model.lr * (mod_post.T @ mod_pre - std_post.T @ std_pre) / _BATCH
            )
            layer.bias.add_(-model.lr * (mod_post.mean(0) - std_post.mean(0)))
        out_layer.weight.add_(-model.lr * error.T @ acts[-1] / _BATCH)
        out_layer.bias.add_(-model.lr * error.mean(0))


def test_pepita_bespoke_step_is_the_store_all_schedule() -> None:
    """The bespoke surface stops before a readout, so both chains get the ReLU."""
    torch.manual_seed(1)
    layers = [torch.nn.Linear(_IN, _HIDDEN), torch.nn.Linear(_HIDDEN, _HIDDEN)]
    out_layer = torch.nn.Linear(_HIDDEN, _OUT)
    model = SimpleNamespace(
        layers=torch.nn.ModuleList(layers),
        out_layer=out_layer,
        feedback_matrix=torch.randn(_IN, _OUT) * 0.1,
        output_dim=_OUT,
        lr=0.01,
    )
    backend = PEPITAKernelBackend()
    backend.initialize(_config(AlgorithmFamily.PEPITA))
    x, y = torch.randn(_BATCH, _IN), torch.randint(0, _OUT, (_BATCH,))
    modules = [*layers, out_layer]
    state = _snapshot(modules)

    _bespoke_store_all(model, backend._scale, x, y)
    stored = _snapshot(modules)
    assert all(
        (weight - start).abs().max() > 0
        for weight, start in zip(stored, state, strict=True)
    ), "the reference rung must move the weights"

    _restore(modules, state)
    metrics = backend.kernel_train_step(model, None, x, y)

    for parameter, weight in zip(
        (p for module in modules for p in module.parameters()), stored, strict=True
    ):
        torch.testing.assert_close(parameter, weight, rtol=0, atol=1e-7)
    assert metrics["accuracy"] >= 0.0


def test_the_claim_path_trains_through_the_lockstep() -> None:
    """Rung 0: the composed system's ``train_step`` reaches the stream and moves."""
    from computronium.acceleration.coordinate import kernel_config_of
    from computronium.core.presets import create_pepita_mlp

    system = create_pepita_mlp(_IN, (_HIDDEN,), _OUT, device="cpu")
    backend = PEPITAKernelBackend()
    backend.initialize(kernel_config_of(system, PEPITAKernelBackend))
    system.attach_kernel_backend(backend)
    before = {name: p.detach().clone() for name, p in system.geometry.params.items()}

    metrics = system.train_step(
        torch.randn(_BATCH, _IN), torch.randint(0, _OUT, (_BATCH,))
    )

    moved = {
        name: float((p - before[name]).abs().max())
        for name, p in system.geometry.params.items()
    }
    assert all(step > 0 for step in moved.values()), moved
    assert metrics["loss"] == metrics["loss"], "the step must report a finite loss"


# --- Depth-flat peak (CUDA) ----------------------------------------------------

_GPU = pytest.mark.skipif(
    not torch.cuda.is_available(), reason="peak memory is a CUDA measurement"
)

_WIDTH, _CLASSES, _PILOT_BATCH = 512, 10, 4096
_DEPTHS = (4, 8, 16, 32)
_ACTIVATION_MB = _PILOT_BATCH * _WIDTH * 4 / 2**20


def _model(family: AlgorithmFamily, depth: int) -> tuple[SimpleNamespace, object]:
    """A bound stack at pilot width; FF embeds labels, PEPITA owns a readout."""
    torch.manual_seed(0)
    if family is AlgorithmFamily.FF:
        stack = [torch.nn.Linear(_WIDTH + _CLASSES, _WIDTH)]
        stack += [torch.nn.Linear(_WIDTH, _WIDTH) for _ in range(depth - 1)]
        backend: object = FFKernelBackend()
        model = SimpleNamespace(
            layers=stack, output_dim=_CLASSES, layer_lr=0.01, input_dim=_WIDTH
        )
    else:
        stack = [torch.nn.Linear(_WIDTH, _WIDTH) for _ in range(depth)]
        backend = PEPITAKernelBackend()
        model = SimpleNamespace(
            layers=stack,
            out_layer=torch.nn.Linear(_WIDTH, _CLASSES),
            feedback_matrix=torch.randn(_WIDTH, _CLASSES) * 0.1,
            output_dim=_CLASSES,
            lr=0.01,
            input_dim=_WIDTH,
        )
    modules = [*model.layers] + (
        [model.out_layer] if family is not AlgorithmFamily.FF else []
    )
    for module in modules:
        module.to("cuda")
    model.layers = torch.nn.ModuleList(model.layers)
    backend.initialize(
        KernelConfig(
            algorithm=family,
            hardware=HardwareTarget.CUDA,
            extra={"input_dim": _WIDTH, "output_dim": _CLASSES},
        )
    )
    return model, backend


def _step_peak_mb(
    family: AlgorithmFamily, depth: int, *, retain: bool = False
) -> float:
    """CUDA peak above the allocated parameters for one lockstep step."""
    model, backend = _model(family, depth)
    x = torch.randn(_PILOT_BATCH, _WIDTH, device="cuda")
    y = torch.randint(0, _CLASSES, (_PILOT_BATCH,), device="cuda")
    torch.cuda.empty_cache()
    torch.cuda.reset_peak_memory_stats()
    base = torch.cuda.memory_allocated()
    real = ff_kernels.lockstep_contrasts
    if retain:
        ff_kernels.lockstep_contrasts = lambda *a, **k: list(real(*a, **k))
    try:
        backend.kernel_train_step(model, None, x, y)
    finally:
        ff_kernels.lockstep_contrasts = real
    peak = (torch.cuda.max_memory_allocated() - base) / 2**20
    del model, x, y
    torch.cuda.empty_cache()
    return peak


@_GPU
@pytest.mark.parametrize("family", [AlgorithmFamily.FF, AlgorithmFamily.PEPITA])
def test_the_lockstep_peak_is_flat_in_depth(family: AlgorithmFamily) -> None:
    """L=4 → L=32 costs no more peak memory than the two chains' buffers."""
    peaks = {depth: _step_peak_mb(family, depth) for depth in _DEPTHS}
    assert peaks[_DEPTHS[-1]] < peaks[_DEPTHS[0]] + 2 * _ACTIVATION_MB, peaks


@_GPU
@pytest.mark.parametrize("family", [AlgorithmFamily.FF, AlgorithmFamily.PEPITA])
def test_retaining_the_contrast_stream_bends_the_peak(
    family: AlgorithmFamily,
) -> None:
    """Negative control: materializing the stream is the store-all rung."""
    lockstep_deep = _step_peak_mb(family, _DEPTHS[-1])
    retained_shallow = _step_peak_mb(family, _DEPTHS[0], retain=True)
    retained_deep = _step_peak_mb(family, _DEPTHS[-1], retain=True)
    assert retained_deep > 2 * lockstep_deep, (retained_deep, lockstep_deep)
    assert retained_deep > 2 * retained_shallow, (retained_deep, retained_shallow)
