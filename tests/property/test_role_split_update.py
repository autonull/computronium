"""Property tests for RoleSplitUpdate (TODO19 R6-A, X-USU-001 promotion).

The dispatcher must behave exactly like running each sub-rule alone on its
own name subset: disjoint ownership, no double-stepping, per-role momentum
state, and a config round-trip through ``dataclasses.asdict``.
"""

from __future__ import annotations

import dataclasses
from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from computronium.ontology.geometry import Geometry

import pytest
import torch
from torch import Tensor

from computronium.ontology.update import (
    ParameterUpdateConfig,
    RoleSplitSpec,
    RoleSplitUpdate,
    update_from_config,
)
from computronium.ontology.utils import _learnable_weight_names

WEIGHT_NAMES = ("0.weight", "1.weight", "2.weight")
ROLE = ("2.weight",)
LR = 0.05
G = cast("Geometry", None)


def _params() -> dict[str, Tensor]:
    torch.manual_seed(7)
    return {
        "0.weight": torch.randn(6, 4),
        "1.weight": torch.randn(8, 6),
        "2.weight": torch.randn(3, 8),
        "0.bias": torch.randn(6),
    }


def _grads(params: dict[str, Tensor]) -> list[Tensor]:
    torch.manual_seed(11)
    grads = {n: torch.randn_like(params[n]) for n in WEIGHT_NAMES}
    return [grads[n] for n in _learnable_weight_names(params)]


def _config(role_names: tuple[str, ...]) -> ParameterUpdateConfig:
    return ParameterUpdateConfig.role_split(
        role_names=role_names,
        on_role=ParameterUpdateConfig.riemannian_orthogonal(step_size=LR, momentum=0.0),
        other=ParameterUpdateConfig.euclidean(
            step_size=LR, momentum=0.0, grad_clip=0.0
        ),
    )


def _spec(cfg: ParameterUpdateConfig) -> RoleSplitSpec:
    assert cfg.sub_rules is not None
    return cfg.sub_rules


class TestPartitionExactness:
    def test_role_names_follow_on_role_rule(self) -> None:
        """Owned names move exactly as the on-role rule alone on that name."""
        params = _params()
        grads = _grads(params)
        out = RoleSplitUpdate(_config(ROLE)).step(params, grads, G)

        muon = update_from_config(_spec(_config(ROLE)).on_role)
        solo = muon.step({"2.weight": params["2.weight"]}, [grads[2]], G)
        assert torch.allclose(out["2.weight"], solo["2.weight"], atol=1e-6)

    def test_other_names_follow_other_rule(self) -> None:
        """Non-role weights move exactly as euclid-alone (param − lr·grad)."""
        params = _params()
        grads = _grads(params)
        out = RoleSplitUpdate(_config(ROLE)).step(params, grads, G)
        for name, grad in zip(WEIGHT_NAMES, grads):
            if name in ROLE:
                continue
            assert torch.allclose(out[name], params[name] - LR * grad, atol=1e-5), name

    def test_biases_pass_through_untouched(self) -> None:
        params = _params()
        out = RoleSplitUpdate(_config(ROLE)).step(params, _grads(params), G)
        assert torch.equal(out["0.bias"], params["0.bias"])

    def test_bias_grads_routed_to_owner(self) -> None:
        params = _params()
        bias = torch.randn(6)
        out = RoleSplitUpdate(_config(("0.bias",))).step(
            params, _grads(params), G, bias_grads={"0.bias": bias}
        )
        assert torch.allclose(out["0.bias"], params["0.bias"] - LR * bias, atol=1e-5)


class TestNoDoubleStepping:
    def test_role_complement_covers_each_weight_once(self) -> None:
        """Flipping the role set to its complement yields identical per-name
        results — each weight is owned by exactly one sub-rule either way."""
        params = _params()
        grads = _grads(params)
        cfg = _config(ROLE)
        spec = _spec(cfg)
        forward = RoleSplitUpdate(cfg).step(params, grads, G)
        flipped = RoleSplitUpdate(
            ParameterUpdateConfig.role_split(
                role_names=("0.weight", "1.weight"),
                on_role=spec.other,
                other=spec.on_role,
            )
        ).step(params, grads, G)
        for name in WEIGHT_NAMES:
            assert torch.allclose(forward[name], flipped[name], atol=1e-6), name


class TestStateRoundTrip:
    def test_snapshot_replay_is_deterministic(self) -> None:
        params = _params()
        grads = _grads(params)
        cfg = ParameterUpdateConfig.role_split(
            role_names=ROLE,
            on_role=ParameterUpdateConfig.riemannian_orthogonal(
                step_size=LR, momentum=0.9
            ),
            other=ParameterUpdateConfig.euclidean(step_size=LR, momentum=0.9),
        )
        split = RoleSplitUpdate(cfg)
        split.step(params, grads, G)
        snapshot = split.get_state()
        first = split.step(params, grads, G)
        split.load_state(snapshot)
        second = split.step(params, grads, G)
        for name in first:
            assert torch.allclose(first[name], second[name], atol=1e-6), name


class TestConfigRoundTrip:
    def test_asdict_round_trip_preserves_dispatch(self) -> None:
        cfg = _config(ROLE)
        restored = ParameterUpdateConfig(**dataclasses.asdict(cfg))
        assert restored.update_type == "role_split"
        assert RoleSplitSpec.coerce(_spec(restored)) == cfg.sub_rules
        a = RoleSplitUpdate(cfg).step(_params(), _grads(_params()), G)
        b = RoleSplitUpdate(restored).step(_params(), _grads(_params()), G)
        for name in a:
            assert torch.equal(a[name], b[name]), name

    def test_factory_dispatch(self) -> None:
        assert isinstance(update_from_config(_config(ROLE)), RoleSplitUpdate)

    def test_rejects_non_role_split_config(self) -> None:
        with pytest.raises(ValueError, match="role_split"):
            RoleSplitUpdate(ParameterUpdateConfig.euclidean())


class TestEndToEnd:
    def test_system_train_step_with_role_split_update(self) -> None:
        """A composed 5-D system with a role-split update runs a train step;
        the readout moves under the muon rule (near-equal row norms)."""
        from computronium.analysis.mechanistic_study import (
            _INPUT_DIM,
            _OUTPUT_DIM,
            _build_system,
        )
        from computronium.ontology.credit import CreditAssignmentConfig

        torch.manual_seed(0)
        system = _build_system(
            CreditAssignmentConfig.random_projections(),
            _config(("2.weight",)),
            seed=0,
        )
        readout_before = system.geometry.params["2.weight"].detach().clone()
        result = system.train_step(
            torch.randn(8, _INPUT_DIM), torch.randint(0, _OUTPUT_DIM, (8,))
        )
        assert "loss" in result
        after = system.geometry.params["2.weight"].detach()
        norms = (after - readout_before).norm(dim=1)
        assert norms.max() / norms.min() < 10.0
