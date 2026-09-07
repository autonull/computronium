"""TODO12b defect-hunt locks (H1/H2/H3/H8 findings, pre-registered).

Locks the CONFIRMED findings of the defect hunt so they can never
silently regress:
- H1: UnitRMSUpdate is bitwise-exact vs the normalize-the-momentum
  reference and converges (cos(step, -grad) -> 1) on a deterministic
  quadratic; the D16 "noise floor" was an lr mislabel, locked here via
  the working-lr MNIST-free surrogate (per-element displacement =
  step_size exactly).
- H2: biases receive no pseudo-gradient in ANY credit (bp included) —
  the weights-only-backprop contract, locked as intentional.
- H3: ThermodynamicContrast under InstantaneousDynamics emits an exact
  ZERO hidden-layer pseudo-gradient (f5b structural fact) — the F5
  Claim-A scope, locked as a standing compatibility entry.
- H8: GradientCredit's nudged loss is the target-blended CE; beta=1.0
  yields an EXACTLY ZERO pseudo-gradient (dead loss surface) — locked
  to forbid beta=1.0 configs.
"""

import pytest
import torch
from torch import nn

from computronium import (
    BackpropCredit,
    DigitalSubstrate,
    EuclideanUpdate,
    FeedforwardGeometry,
    GeometryConfig,
    InstantaneousDynamics,
    StateDynamicsConfig,
    SubstrateConfig,
    compose_system,
)
from computronium.core.pipeline import forward_pass, task_loss
from computronium.ontology.credit import Phase
from computronium.ontology.system import SystemConfig, SystemState
from computronium.ontology.update import ParameterUpdateConfig, UnitRMSUpdate
from computronium.ontology.utils import _learnable_weight_names


def _system(credit, beta: float = 0.5):
    return compose_system(
        substrate=DigitalSubstrate(SubstrateConfig.digital(device="cpu")),
        geometry=FeedforwardGeometry(
            GeometryConfig.feedforward(input_dim=20, output_dim=8, hidden_dims=(16,))
        ),
        dynamics=InstantaneousDynamics(StateDynamicsConfig.instantaneous(beta=beta)),
        credit=credit,
        update=EuclideanUpdate(),
    )


def _phases(system, x: torch.Tensor, y: torch.Tensor):
    states: dict[Phase, SystemState] = {}
    loss = None
    initial = forward_pass(system.substrate, system.geometry, x)
    for phase in system.credit.phases:
        state = SystemState(x=x, y=y)
        state.activations = initial
        settled = system.dynamics.settle(
            state,
            system.geometry,
            system.substrate,
            target=y if phase is Phase.NUDGED else None,
        )
        if phase is Phase.NUDGED:
            settled.loss = task_loss(settled, y)
            loss = settled.loss
        states[phase] = settled
    return states, loss


class TestH1UnitRMSExact:
    def test_bitwise_reference(self) -> None:
        torch.manual_seed(1)
        upd = UnitRMSUpdate(ParameterUpdateConfig.unit_rms(step_size=0.1, momentum=0.9))
        lr, m = 0.1, 0.9
        p = torch.randn(8, 4)
        buf = torch.zeros_like(p)
        for _ in range(5):
            g = torch.randn_like(p)
            new = upd.step({"0.weight": p.clone()}, [g.clone()], None)["0.weight"]  # type: ignore[arg-type]
            buf.mul_(m).add_(g)
            ref = p - lr * buf / buf.square().mean().sqrt().add_(1e-8)
            assert torch.equal(new, ref)
            p = new

    def test_quadratic_direction_and_bounded_drift(self) -> None:
        torch.manual_seed(0)
        a = torch.linspace(0.1, 1.0, 64)
        params = {"0.weight": torch.ones(1, 64)}
        upd = UnitRMSUpdate(ParameterUpdateConfig.unit_rms(step_size=0.3, momentum=0.9))
        f0 = (0.5 * a * params["0.weight"].squeeze() ** 2).sum().item()
        cosines: list[float] = []
        for _ in range(400):
            x = params["0.weight"]
            g = (a * x).reshape(1, 64)
            step = upd.step(params, [g], None)["0.weight"]  # type: ignore[arg-type]
            delta = (step - x).squeeze()
            cosines.append(
                (
                    torch.dot(delta, -g.squeeze()) / (delta.norm() * g.norm() + 1e-12)
                ).item()
            )
            params["0.weight"] = step
        f1 = (0.5 * a * params["0.weight"].squeeze() ** 2).sum().item()
        assert torch.isfinite(torch.tensor(f1))
        assert f1 < f0 * 0.05  # converged to the lr-ball, no divergence
        assert sum(cosines[-100:]) / 100 > 0.9  # EMA direction converges

    def test_per_element_displacement_is_step_size(self) -> None:
        """The D16 lesson: unit_rms's lr is per-element displacement."""
        torch.manual_seed(2)
        upd = UnitRMSUpdate()
        p = torch.randn(32, 16)
        g = torch.randn_like(p)
        new = upd.step({"0.weight": p}, [g], None)["0.weight"]  # type: ignore[arg-type]
        delta = new - p
        rms = delta.pow(2).mean().sqrt().item()
        assert abs(rms - 0.01) < 1e-6  # == default step_size


class TestH2BiasFreezeContract:
    def test_learnable_names_exclude_biases(self) -> None:
        params = {
            "0.weight": torch.zeros(4, 4),
            "0.bias": torch.zeros(4),
            "1.weight": torch.zeros(2, 4),
            "1.bias": torch.zeros(2),
        }
        assert _learnable_weight_names(params) == ["0.weight", "1.weight"]

    def test_backprop_credit_emits_no_bias_grads(self) -> None:
        torch.manual_seed(0)
        system = _system(BackpropCredit())
        x = torch.randn(4, 20)
        y = torch.randint(0, 8, (4,))
        states, loss = _phases(system, x, y)
        grads = system.credit.compute_pseudo_gradient(states, loss, system.geometry)
        weight_names = _learnable_weight_names(system.geometry.params)
        assert set(weight_names) == {"0.weight", "2.weight"}
        assert len(grads) == len(weight_names)
        # Bias params untouched by the update path (apply_pseudo_gradients
        # passes them through) — the weights-only-backprop contract.
        bias_pre = {n: system.geometry.params[n].clone() for n in ("0.bias", "2.bias")}
        system.geometry.update_params(
            EuclideanUpdate().step(system.geometry.params, grads, system.geometry)
        )
        for name, pre in bias_pre.items():
            assert torch.equal(system.geometry.params[name], pre)


class TestH3ThermoInstantaneousHiddenZero:
    def test_hidden_layer_pseudo_gradient_is_exact_zero(self) -> None:
        from computronium import ThermodynamicContrast

        torch.manual_seed(0)
        system = _system(ThermodynamicContrast())
        x = torch.randn(4, 20)
        y = torch.randint(0, 8, (4,))
        states, loss = _phases(system, x, y)
        grads = system.credit.compute_pseudo_gradient(states, loss, system.geometry)
        assert grads[0].abs().max().item() == 0.0  # ruff: ignore[float-equality-comparison] — exact structural zero
        assert grads[1].abs().max().item() > 0.0  # output: live


class TestH8ClampedCE:
    def test_beta_one_is_dead_loss_surface(self) -> None:
        torch.manual_seed(0)
        net = nn.Sequential(nn.Linear(20, 16), nn.ReLU(), nn.Linear(16, 8))
        x = torch.randn(4, 20)
        y = torch.randint(0, 8, (4,))
        onehot = torch.nn.functional.one_hot(y, 8).float()
        free = net(x)
        clamped = free + 1.0 * (onehot - free)
        g = torch.autograd.grad(
            nn.functional.cross_entropy(clamped, y),
            list(net.parameters()),
            allow_unused=True,
        )
        assert all(
            gi is None or gi.abs().max().item() == 0.0  # ruff: ignore[float-equality-comparison] — exact zero
            for gi in g
        )

    def test_default_beta_preserves_direction(self) -> None:
        torch.manual_seed(0)
        net = nn.Sequential(nn.Linear(20, 16), nn.ReLU(), nn.Linear(16, 8))
        x = torch.randn(4, 20)
        y = torch.randint(0, 8, (4,))
        onehot = torch.nn.functional.one_hot(y, 8).float()
        free = net(x)
        clamped = free + 0.5 * (onehot - free)
        ce = nn.functional.cross_entropy
        g_free = torch.autograd.grad(
            ce(free, y), list(net.parameters()), retain_graph=True
        )
        g_clamp = torch.autograd.grad(ce(clamped, y), list(net.parameters()))
        for a, b in zip(g_free, g_clamp, strict=True):
            cos = torch.dot(a.flatten(), b.flatten()) / (a.norm() * b.norm() + 1e-12)
            assert cos.item() > 0.98


def _config(credit, update):
    from computronium import CreditAssignmentConfig

    return SystemConfig(
        substrate=SubstrateConfig.digital(),
        geometry=GeometryConfig.feedforward(
            input_dim=20, output_dim=8, hidden_dims=(16,)
        ),
        dynamics=StateDynamicsConfig.instantaneous(),
        credit=credit.config
        if credit is not None
        else CreditAssignmentConfig.gradient(),
        update=update,
    )


class TestR5StepSemantics:
    def test_family_classification(self) -> None:
        assert ParameterUpdateConfig.euclidean().step_semantics == "gradient_relative"
        for cfg in (
            ParameterUpdateConfig.adam(),
            ParameterUpdateConfig.local_adam(),
            ParameterUpdateConfig.ortho_adam(),
            ParameterUpdateConfig.unit_rms(),
            ParameterUpdateConfig.mean_norm(),
            ParameterUpdateConfig.riemannian_orthogonal(),
            ParameterUpdateConfig.spectral_constrained(),
            ParameterUpdateConfig.elastic_consolidation(),
        ):
            assert cfg.step_semantics == "per_element_displacement", cfg.update_type

    def test_validate_warns_on_borrowed_lr_grid(self) -> None:
        with pytest.warns(UserWarning, match="per-element-displacement"):
            _config(None, ParameterUpdateConfig.unit_rms(step_size=0.1)).validate()

    def test_validate_silent_at_working_lr(self) -> None:
        _config(None, ParameterUpdateConfig.unit_rms(step_size=0.02)).validate()


class TestH8ConfigGuard:
    def test_validate_rejects_beta_one(self) -> None:
        system = _config(BackpropCredit(), ParameterUpdateConfig.euclidean())
        object.__setattr__(system.credit, "beta", 1.0)
        with pytest.raises(ValueError, match="exactly-zero pseudo-gradient"):
            system.validate()
