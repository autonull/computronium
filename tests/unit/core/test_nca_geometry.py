"""NcaGeometry behavior tests (TODO.ntm_nca.md §10 item 1 promotion)."""

import pytest
import torch
import torch.nn.functional as F  # ruff: ignore[lowercase-imported-as-non-lowercase]
from torch import Tensor

from computronium import (
    GeometryConfig,
    NcaGeometry,
    ParameterUpdateConfig,
    StateDynamicsConfig,
    SubstrateConfig,
    SystemConfig,
)
from computronium.ontology.geometry import geometry_from_config
from computronium.ontology.utils.params import apply_pseudo_gradients

GRID = 10
CHANNELS = 4


def _geometry(**kwargs) -> NcaGeometry:
    config = GeometryConfig.nca(channels=CHANNELS, grid_hw=(GRID, GRID), **kwargs)
    geometry = geometry_from_config(config)
    assert isinstance(geometry, NcaGeometry)
    return geometry


def _ring_targets() -> Tensor:
    i = torch.arange(GRID).view(-1, 1)
    j = torch.arange(GRID).view(1, -1)
    c = (GRID - 1) / 2
    ring = (((i - c).abs() - 2).abs() <= 1) & (((j - c).abs() - 2).abs() <= 1)
    ids = ring.long() + 1  # fg cells -> class 1..3, bg -> 0
    return ids.clamp(0, CHANNELS - 1)


def _seed_states(targets: Tensor) -> Tensor:
    states = torch.zeros(1, CHANNELS, GRID, GRID)
    y, x = GRID // 2, GRID // 2
    states[:, :, y, x] = torch.eye(CHANNELS)[targets[y, x]]
    return states


def _label_grid(targets: Tensor) -> Tensor:
    """(H, W) class ids -> (1, C, H, W) one-hot label grid."""
    return (
        torch.nn.functional
        .one_hot(targets.unsqueeze(0), CHANNELS)
        .permute(0, 3, 1, 2)
        .float()
    )


class TestNcaStep:
    def test_step_shape_and_delta_bound(self) -> None:
        torch.manual_seed(0)
        geometry = _geometry()
        states = torch.randn(2, CHANNELS, GRID, GRID)
        next_states = geometry.step(states)
        assert next_states.shape == states.shape
        delta = next_states - states
        assert delta.abs().max() <= geometry.config.delta_scale + 1e-6

    def test_explicit_mask_is_spatially_exact(self) -> None:
        torch.manual_seed(0)
        geometry = _geometry()
        states = torch.randn(1, CHANNELS, GRID, GRID)
        mask = torch.zeros(GRID, GRID)
        mask[3, 3] = 1.0
        next_states = geometry.step(states, mask=mask)
        assert torch.equal(next_states[:, :, 0, 0], states[:, :, 0, 0])
        assert (next_states[:, :, 3, 3] - states[:, :, 3, 3]).abs().sum() > 0

    def test_rollout_no_grad_matches_step_loop(self) -> None:
        torch.manual_seed(0)
        geometry = _geometry(mask_prob=1.0)
        states = _seed_states(_ring_targets())
        expected = states
        for _ in range(3):
            expected = geometry.step(expected)
        torch.manual_seed(7)
        assert torch.allclose(geometry.rollout(states, 3), expected)

    def test_update_params_round_trip(self) -> None:
        torch.manual_seed(0)
        geometry = _geometry()
        clone = _geometry()
        clone.update_params(geometry.params)
        for name, tensor in geometry.params.items():
            assert torch.equal(clone.params[name], tensor)


class TestNcaCreditUpdateComposition:
    def test_pseudo_gradient_update_moves_weights(self) -> None:
        torch.manual_seed(0)
        geometry = _geometry(mask_prob=1.0, label_channels=CHANNELS)
        params = {
            k: v.detach().clone().requires_grad_(True)
            for k, v in geometry.params.items()
        }
        states = _seed_states(_ring_targets())
        labels = _label_grid(_ring_targets())

        def _delta_with(p: dict[str, Tensor]) -> Tensor:
            x = geometry.perceive(states, labels)
            h = torch.relu(F.linear(x, p["cell_hidden_weight"], p["cell_hidden_bias"]))
            d = F.linear(h, p["cell_delta_weight"], p["cell_delta_bias"])
            return geometry.config.delta_scale * torch.tanh(d)

        for _ in range(4):
            with torch.enable_grad():
                next_states = states + _delta_with(params).view_as(states)
            loss = (next_states - states).pow(2).mean()
            grads = torch.autograd.grad(loss, list(params.values()), allow_unused=True)
            weight_grads = [
                g
                for n, g in zip(params, grads, strict=True)
                if "weight" in n and g is not None
            ]
            assert weight_grads and any(g.abs().sum() > 0 for g in weight_grads)
            bias_grads = {
                n: g
                for n, g in zip(params, grads, strict=True)
                if "bias" in n and g is not None
            }
            new = apply_pseudo_gradients(
                params, weight_grads, lambda _n, p, g: p - 0.05 * g, bias_grads
            )
            params = {
                k: v.detach().clone().requires_grad_(True) for k, v in new.items()
            }
            states = next_states.detach()
        assert any(
            not torch.equal(params[n], geometry.params[n])
            for n in params
            if "weight" in n
        )

    def test_system_config_rejects_non_instantaneous_dynamics(self) -> None:
        config = SystemConfig(
            substrate=SubstrateConfig.digital(),
            geometry=GeometryConfig.nca(channels=CHANNELS),
            dynamics=StateDynamicsConfig.energy_minimization(),
            credit=_credit(),
            update=ParameterUpdateConfig.euclidean(),
        )
        with pytest.raises(ValueError, match="NCA geometry requires instantaneous"):
            config.validate()


def _credit():
    from computronium import CreditAssignmentConfig

    return CreditAssignmentConfig.gradient()


class TestNcaDistillInit:
    def test_distill_then_grow(self) -> None:
        torch.manual_seed(0)
        geometry = _geometry(mask_prob=0.5, label_channels=CHANNELS)
        targets = _ring_targets()
        labels = _label_grid(targets)
        target_states = labels.clone()
        mse = geometry.distill_init(
            target_states,
            labels,
            seed_states=_seed_states(targets),
            n_mixes=8,
            steps=1200,
        )
        assert mse < 0.01
        final = geometry.rollout(_seed_states(targets), 32, labels)
        acc = (final.argmax(1) == targets).float().mean()
        assert acc > 0.7, (
            f"distilled controller failed to grow (acc {acc:.3f}, mse {mse:.5f})"
        )
