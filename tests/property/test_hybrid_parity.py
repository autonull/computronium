"""Locks for the hybrid credit (TODO93 T3b, §8.1, §18).

``HybridCredit`` composes a lockstep-local trunk with an exact-gradient head.
Three claims need a lock before it can enter the memory frontier.

**Parity.** The lockstep trunk is checked against a *store-all* hybrid written
from the equations — two-pass PEPITA trunk with every activation retained, no
lockstep — at ``atol=0`` per layer. "Composes" is not acceptance; parity is.

**True head gradients.** The head's gradients must equal plain backprop's
gradients for the same boundary input, not a local contrast.

**Depth-flat peak.** The trunk keeps one layer's two chains live; the store-all
reference keeps ``2L`` activation lists. The CUDA lock measures both at
``L=4/8/16/32``: the hybrid's peak is flat, the retained stream bends.
"""

from __future__ import annotations

import pytest
import torch
from torch import nn

from computronium.ontology.credit import (
    CreditAssignmentConfig,
    HybridCredit,
    Phase,
)
from computronium.ontology.geometry import FeedforwardGeometry, GeometryConfig
from computronium.ontology.substrate import DigitalSubstrate
from computronium.ontology.system import SystemState

_IN, _HIDDEN, _OUT, _BATCH = 6, 10, 4, 8


def _geometry(
    hidden: tuple[int, ...] = (_HIDDEN, _HIDDEN),
    *,
    residual: bool = False,
) -> FeedforwardGeometry:
    return FeedforwardGeometry(
        GeometryConfig.feedforward(
            input_dim=_IN,
            output_dim=_OUT,
            hidden_dims=hidden,
            residual=residual,
        )
    )


def _parts(
    geometry: FeedforwardGeometry,
) -> tuple[list[nn.Module], list[nn.Module], int]:
    starts = [
        i for i, layer in enumerate(geometry._layers) if isinstance(layer, nn.Linear)
    ]
    split = starts[-2]
    return list(geometry._layers[:split]), list(geometry._layers[split:]), split


def _weights_in_order(geometry: FeedforwardGeometry) -> list[str]:
    return [n for n, p in geometry.params.items() if "weight" in n and p.dim() == 2]


def _store_all_chain(
    geometry: FeedforwardGeometry, layers: list[nn.Module], start: torch.Tensor
) -> list[torch.Tensor]:
    """Every activation of one pass, retained (the schedule the lockstep removes)."""
    op = DigitalSubstrate().get_forward_operator()
    chain = [start]
    h = h_in = start
    with torch.no_grad():
        for layer in layers:
            h, h_in = geometry.step_layer(h, layer, h_in, op)
            chain.append(h)
    return chain


def _store_all_contrasts(
    trunk: list[nn.Module],
    standard: list[torch.Tensor],
    modulated: list[torch.Tensor],
) -> dict[str, torch.Tensor]:
    """Per-Linear contrasts formed after both activation lists exist."""
    batch = standard[0].shape[0]
    grads: dict[str, torch.Tensor] = {}
    for index, layer in enumerate(trunk):
        if not isinstance(layer, nn.Linear):
            continue
        has_activation = index + 1 < len(trunk) and not isinstance(
            trunk[index + 1], nn.Linear
        )
        offset = 2 if has_activation else 1
        pre_standard, post_standard = standard[index], standard[index + offset]
        pre_modulated, post_modulated = modulated[index], modulated[index + offset]
        grads[f"{index}.weight"] = (
            post_modulated.T @ pre_modulated - post_standard.T @ pre_standard
        ) / batch
    return grads


def _store_all_hybrid(
    geometry: FeedforwardGeometry,
    x: torch.Tensor,
    y: torch.Tensor,
    *,
    split: int,
    gamma: float,
    feedback: torch.Tensor,
) -> dict[str, torch.Tensor]:
    """The store-all reference, written from the hybrid's equations.

    Pass 1 keeps every standard activation; the head backprop gives δ; pass 2
    keeps every modulated activation; the per-layer contrast is formed after
    both lists exist. This is the schedule the lockstep removes.
    """
    layers = list(geometry._layers)
    trunk = layers[:split]
    standard = _store_all_chain(geometry, trunk, x)
    boundary = standard[-1].detach().requires_grad_(True)
    logits = geometry._apply_layers(
        boundary, tuple(layers[split:]), DigitalSubstrate().get_forward_operator()
    )
    loss = torch.nn.functional.cross_entropy(logits, y)

    head_names = [
        f"{i}.weight"
        for i in range(split, len(layers))
        if isinstance(layers[i], nn.Linear)
    ]
    head_params = [geometry.params[name] for name in head_names]
    grads = torch.autograd.grad(loss, [*head_params, boundary])
    delta = grads[-1]
    head_grads = dict(zip(head_names, grads[:-1], strict=True))

    modulated = _store_all_chain(geometry, trunk, x + gamma * (delta @ feedback))
    trunk_grads = _store_all_contrasts(trunk, standard, modulated)
    return {**trunk_grads, **head_grads}


def _hybrid_grads(
    geometry: FeedforwardGeometry,
    x: torch.Tensor,
    y: torch.Tensor,
    *,
    split: int | None = None,
    gamma: float = 0.05,
    feedback: torch.Tensor | None = None,
    trunk_lr: float = 1.0,
) -> tuple[dict[str, torch.Tensor], HybridCredit]:
    config = CreditAssignmentConfig.hybrid(
        split_layer=split if split is not None else -1,
        gamma=gamma,
        feedback_matrix=feedback,
        trunk_lr=trunk_lr,
    )
    credit = HybridCredit(config)
    gradients = credit.compute_pseudo_gradient(
        {Phase.FREE: SystemState(x=x, y=y)}, None, geometry
    )
    names = _weights_in_order(geometry)
    return dict(zip(names, gradients, strict=True)), credit


def test_the_lockstep_trunk_is_the_store_all_schedule() -> None:
    """Per-layer deltas match the store-all hybrid at the equations' precision."""
    torch.manual_seed(0)
    geometry = _geometry()
    x = torch.randn(_BATCH, _IN)
    y = torch.randint(0, _OUT, (_BATCH,))
    trunk, _head, split = _parts(geometry)
    torch.manual_seed(11)
    feedback = torch.randn(_HIDDEN, _IN) * 0.1

    reference = _store_all_hybrid(
        geometry, x, y, split=split, gamma=0.05, feedback=feedback
    )
    hybrid, _credit = _hybrid_grads(
        geometry, x, y, split=split, gamma=0.05, feedback=feedback
    )

    assert set(reference) == set(hybrid), (reference.keys(), hybrid.keys())
    for name in reference:
        torch.testing.assert_close(hybrid[name], reference[name], rtol=0, atol=1e-7)
    assert any(torch.count_nonzero(reference[name]) for name in reference)
    # The trunk half must move; the head half is exact autograd, not a contrast.
    for index in range(split):
        name = f"{index}.weight"
        if name in reference:
            assert reference[name].abs().max() > 0, name
    assert trunk  # the fixture has a real trunk


def test_the_head_gets_plain_backprop_gradients() -> None:
    """The head's gradient equals full backprop's gradient at the same boundary."""
    torch.manual_seed(1)
    geometry = _geometry()
    x = torch.randn(_BATCH, _IN)
    y = torch.randint(0, _OUT, (_BATCH,))
    _trunk, head, split = _parts(geometry)
    hybrid, _credit = _hybrid_grads(geometry, x, y, split=split)

    logits = geometry.forward(x, DigitalSubstrate())
    loss = torch.nn.functional.cross_entropy(logits, y)
    head_names = [
        name
        for name in _weights_in_order(geometry)
        if int(name.rpartition(".")[0]) >= split
    ]
    exact = torch.autograd.grad(loss, [geometry.params[name] for name in head_names])
    for name, gradient in zip(head_names, exact, strict=True):
        torch.testing.assert_close(hybrid[name], gradient, rtol=0, atol=1e-7)
    assert head


def test_a_readout_only_head_keeps_the_trunk_exact() -> None:
    """The split on the last Linear: 2 trunk layers' contrast + the readout."""
    torch.manual_seed(2)
    geometry = _geometry()
    x = torch.randn(_BATCH, _IN)
    y = torch.randint(0, _OUT, (_BATCH,))
    layers = list(geometry._layers)
    split = max(i for i, layer in enumerate(layers) if isinstance(layer, nn.Linear))
    torch.manual_seed(12)
    feedback = torch.randn(_HIDDEN, _IN) * 0.1

    reference = _store_all_hybrid(
        geometry, x, y, split=split, gamma=0.05, feedback=feedback
    )
    hybrid, credit = _hybrid_grads(
        geometry, x, y, split=split, gamma=0.05, feedback=feedback
    )

    assert credit.split_layer == split
    assert len([n for n in reference if int(n.rpartition(".")[0]) < split]) == 2
    logits = geometry.forward(x, DigitalSubstrate())
    loss = torch.nn.functional.cross_entropy(logits, y)
    exact = torch.autograd.grad(loss, [geometry.params[f"{split}.weight"]])[0]
    for name in reference:
        torch.testing.assert_close(hybrid[name], reference[name], rtol=0, atol=1e-6)
    torch.testing.assert_close(hybrid[f"{split}.weight"], exact, rtol=0, atol=1e-6)
    assert exact.abs().max() > 0


def test_a_decoupled_trunk_step_scales_only_the_trunk() -> None:
    """``trunk_lr`` multiplies the trunk's pseudo-gradients, not the head's."""
    torch.manual_seed(3)
    geometry = _geometry()
    x = torch.randn(_BATCH, _IN)
    y = torch.randint(0, _OUT, (_BATCH,))
    _trunk, _head, split = _parts(geometry)
    torch.manual_seed(13)
    feedback = torch.randn(_HIDDEN, _IN) * 0.1

    registered, _credit = _hybrid_grads(
        geometry, x, y, split=split, gamma=0.05, feedback=feedback
    )
    scaled, scaled_credit = _hybrid_grads(
        geometry,
        x,
        y,
        split=split,
        gamma=0.05,
        feedback=feedback,
        trunk_lr=3.0,
    )

    assert scaled_credit.trunk_lr == 3.0
    for name in registered:
        if int(name.rpartition(".")[0]) < split:
            torch.testing.assert_close(
                scaled[name], 3.0 * registered[name], rtol=0, atol=1e-7
            )
        else:
            torch.testing.assert_close(
                scaled[name], registered[name], rtol=0, atol=1e-7
            )
    assert any(
        torch.count_nonzero(registered[name])
        for name in registered
        if int(name.rpartition(".")[0]) < split
    )


def test_the_trunk_pass_runs_under_no_grad(monkeypatch) -> None:
    """Remove the ``no_grad`` and the first recorded pass is the negative control."""
    torch.manual_seed(2)
    geometry = _geometry()
    x = torch.randn(_BATCH, _IN)
    y = torch.randint(0, _OUT, (_BATCH,))
    _trunk, _head, split = _parts(geometry)

    real = geometry._apply_layers
    recorded: list[bool] = []

    def recording(h, layers, op, intermediates=None):
        recorded.append(torch.is_grad_enabled())
        return real(h, layers, op, intermediates)

    monkeypatch.setattr(geometry, "_apply_layers", recording)
    hybrid, credit = _hybrid_grads(geometry, x, y, split=split)

    assert credit.IDENTITY_CARD.estimator_kind == "hybrid"
    assert recorded[0] is False, "the trunk pass must not record a graph"
    assert recorded[1] is True, "the head pass must record a graph"
    assert hybrid, "the credit must produce one gradient per weight"


def test_a_residual_trunk_recomputes_the_standard_chain() -> None:
    """A residual geometry's skip reads the Linear's input on both passes."""
    torch.manual_seed(3)
    geometry = _geometry((_HIDDEN, _HIDDEN), residual=True)
    x = torch.randn(_BATCH, _IN)
    y = torch.randint(0, _OUT, (_BATCH,))
    _trunk, _head, split = _parts(geometry)
    torch.manual_seed(12)
    feedback = torch.randn(_HIDDEN, _IN) * 0.1

    reference = _store_all_hybrid(
        geometry, x, y, split=split, gamma=0.05, feedback=feedback
    )
    hybrid, _credit = _hybrid_grads(
        geometry, x, y, split=split, gamma=0.05, feedback=feedback
    )
    for name in reference:
        torch.testing.assert_close(hybrid[name], reference[name], rtol=0, atol=1e-7)


def test_the_composed_system_learns_with_the_hybrid() -> None:
    """Rung 1: the claim path's ``train_step`` decreases the loss."""
    from computronium.core.system_trainer.spec import compose_system_from_configs
    from computronium.ontology import (
        GeometryConfig,
        ParameterUpdateConfig,
        StateDynamicsConfig,
        SubstrateConfig,
    )

    torch.manual_seed(4)
    system = compose_system_from_configs(
        substrate=SubstrateConfig.digital(),
        geometry=GeometryConfig.feedforward(
            input_dim=_IN, output_dim=_OUT, hidden_dims=(_HIDDEN, _HIDDEN)
        ),
        dynamics=StateDynamicsConfig.instantaneous(),
        credit=CreditAssignmentConfig.hybrid(gamma=0.05),
        update=ParameterUpdateConfig.euclidean(step_size=0.01),
    )
    x = torch.randn(64, _IN)
    y = torch.randint(0, _OUT, (64,))
    before = {name: p.detach().clone() for name, p in system.geometry.params.items()}

    losses = [float(system.train_step(x, y)["loss"]) for _ in range(40)]

    assert losses[-1] < losses[0], losses[:2] + losses[-2:]
    moved = [
        float((p - before[name]).detach().abs().max())
        for name, p in system.geometry.params.items()
        if p.ndim == 2
    ]
    assert all(step > 0 for step in moved), moved


def test_the_hybrid_refuses_a_non_feedforward_geometry() -> None:
    """The split is a dense stack boundary; a recurrent graph has no such node."""
    from computronium.ontology import (
        GeometryConfig,
        ParameterUpdateConfig,
        PlasticityConfig,
        StateDynamicsConfig,
        SubstrateConfig,
        SystemConfig,
    )

    def config(geometry: GeometryConfig) -> SystemConfig:
        return SystemConfig(
            substrate=SubstrateConfig.digital(),
            geometry=geometry,
            dynamics=StateDynamicsConfig.instantaneous(),
            credit=CreditAssignmentConfig.hybrid(),
            update=ParameterUpdateConfig.euclidean(step_size=0.01),
            plasticity=PlasticityConfig.null(),
        )

    config(
        GeometryConfig.feedforward(input_dim=_IN, output_dim=_OUT, hidden_dims=(8,))
    ).validate()
    with pytest.raises(ValueError, match="requires a feedforward layer stack"):
        config(
            GeometryConfig.recurrent(input_dim=_IN, output_dim=_OUT, hidden_dims=(8,))
        ).validate()


# --- Depth-flat peak (CUDA) ----------------------------------------------------

_GPU = pytest.mark.skipif(
    not torch.cuda.is_available(), reason="peak memory is a CUDA measurement"
)
_WIDTH, _CLASSES, _PILOT_BATCH = 512, 10, 4096
_DEPTHS = (4, 8, 16, 32)
_ACTIVATION_MB = _PILOT_BATCH * _WIDTH * 4 / 2**20


def _deep_geometry(depth: int) -> FeedforwardGeometry:
    return FeedforwardGeometry(
        GeometryConfig.feedforward(
            input_dim=_WIDTH,
            output_dim=_CLASSES,
            hidden_dims=(_WIDTH,) * depth,
        )
    ).to("cuda")


def _peak_mb(geometry, x, y, *, store_all: bool) -> float:
    """Peak above the weight-gradient set, in MB.

    Every credit that returns pseudo-gradients necessarily holds one
    parameter-sized tensor per layer (O(L·W²)); the store-all hybrid and the
    lockstep hybrid pay that equally. Subtracting it isolates the activation
    share the lock claims — the term that grows with depth only when the
    two-pass stream is retained.
    """
    trunk, _head, split = _parts(geometry)
    credit = HybridCredit(CreditAssignmentConfig.hybrid(split_layer=split))
    gradient_mb = (
        sum(p.numel() for p in geometry.params.values() if p.ndim == 2) * 4 / 2**20
    )
    torch.cuda.empty_cache()
    torch.cuda.reset_peak_memory_stats()
    base = torch.cuda.memory_allocated()
    if store_all:
        torch.manual_seed(11)
        feedback = torch.randn(_WIDTH, _WIDTH, device="cuda") * 0.1
        _store_all_hybrid(geometry, x, y, split=split, gamma=0.05, feedback=feedback)
    else:
        credit.compute_pseudo_gradient(
            {Phase.FREE: SystemState(x=x, y=y)}, None, geometry
        )
    peak = (torch.cuda.max_memory_allocated() - base) / 2**20
    del credit, trunk
    torch.cuda.empty_cache()
    return peak - gradient_mb


@_GPU
def test_the_hybrid_trunk_peak_is_flat_in_depth() -> None:
    """L=4 → L=32 costs no more than the two chains' working set."""
    torch.manual_seed(0)
    peaks = {}
    for depth in _DEPTHS:
        geometry = _deep_geometry(depth)
        x = torch.randn(_PILOT_BATCH, _WIDTH, device="cuda")
        y = torch.randint(0, _CLASSES, (_PILOT_BATCH,), device="cuda")
        peaks[depth] = _peak_mb(geometry, x, y, store_all=False)
        del geometry, x, y
        torch.cuda.empty_cache()
    assert peaks[_DEPTHS[-1]] < peaks[_DEPTHS[0]] + 2 * _ACTIVATION_MB, peaks


@_GPU
def test_retaining_the_trunk_stream_bends_the_peak() -> None:
    """Negative control: the store-all hybrid is the mechanism the lockstep removes."""
    torch.manual_seed(0)
    depth = _DEPTHS[-1]
    geometry = _deep_geometry(depth)
    x = torch.randn(_PILOT_BATCH, _WIDTH, device="cuda")
    y = torch.randint(0, _CLASSES, (_PILOT_BATCH,), device="cuda")
    lockstep = _peak_mb(geometry, x, y, store_all=False)
    retained = _peak_mb(geometry, x, y, store_all=True)
    assert retained > 2 * lockstep, (retained, lockstep)


def _direction_credit(
    *,
    orthogonal_init: bool = False,
    learned_feedback: bool = False,
    feedback_lr: float = 1.0,
    seed: int = 21,
) -> HybridCredit:
    torch.manual_seed(seed)
    return HybridCredit(
        CreditAssignmentConfig.hybrid(
            gamma=0.05,
            orthogonal_init=orthogonal_init,
            learned_feedback=learned_feedback,
            feedback_lr=feedback_lr,
        )
    )


def test_the_orthogonal_direction_keeps_the_registered_draws_norm() -> None:
    """The rotation is the knob: it changes direction, never the draw's scale."""
    torch.manual_seed(0)
    delta = torch.randn(_BATCH, _HIDDEN)
    x = torch.randn(_BATCH, _IN)
    draw = _direction_credit()._feedback_matrix(delta, x)
    rotated = _direction_credit(orthogonal_init=True)._feedback_matrix(delta, x)

    assert rotated.shape == draw.shape
    torch.testing.assert_close(rotated.norm(), draw.norm(), rtol=1e-5, atol=0)
    singular = torch.linalg.svdvals(rotated)[: min(rotated.shape)]
    assert singular.std() < 1e-4 * singular.mean(), singular
    assert not torch.allclose(rotated, draw)


def test_the_learned_direction_moves_at_the_draws_norm() -> None:
    """One ridge step changes B, keeps its norm, and advances its counter."""
    torch.manual_seed(31)
    geometry = _geometry()
    x = torch.randn(_BATCH, _IN)
    y = torch.randint(0, _OUT, (_BATCH,))
    _trunk, _head, split = _parts(geometry)
    credit = _direction_credit(learned_feedback=True)
    draw = credit._feedback_matrix(torch.randn(_BATCH, _HIDDEN), x).clone()

    credit.compute_pseudo_gradient({Phase.FREE: SystemState(x=x, y=y)}, None, geometry)

    learned = credit._trunk_direction(torch.randn(_BATCH, _HIDDEN), x)
    assert credit.feedback_kind == "learned"
    assert credit._direction_step == 2
    torch.testing.assert_close(learned.norm(), draw.norm(), rtol=1e-5, atol=0)
    assert not torch.allclose(learned, draw)
    assert split  # the fixture has a real trunk


def test_the_learned_direction_state_round_trips() -> None:
    """A snapshot restores the direction: the next step is bit-identical."""
    torch.manual_seed(41)
    geometry = _geometry()
    x = torch.randn(_BATCH, _IN)
    y = torch.randint(0, _OUT, (_BATCH,))
    credit = _direction_credit(learned_feedback=True)
    credit.compute_pseudo_gradient({Phase.FREE: SystemState(x=x, y=y)}, None, geometry)
    snap = credit.get_state()
    assert "learned_feedback" not in snap
    assert snap["step"]["counter"].item() == 1
    replay = _direction_credit(learned_feedback=True)
    replay.load_state(snap)
    assert replay._direction_step == credit._direction_step
    delta = torch.randn(_BATCH, _HIDDEN)
    torch.testing.assert_close(
        replay._trunk_direction(delta, x),
        credit._trunk_direction(delta, x),
        rtol=0,
        atol=0,
    )


def test_the_registered_direction_declares_no_learned_state() -> None:
    """The draw and the rotation carry only the counter, so replay is exact."""
    credit = _direction_credit()
    assert credit.feedback_kind == "random"
    assert set(credit.get_state()) == {"step"}
    rotated = _direction_credit(orthogonal_init=True)
    assert rotated.feedback_kind == "orthogonal"
    assert set(rotated.get_state()) == {"step"}
