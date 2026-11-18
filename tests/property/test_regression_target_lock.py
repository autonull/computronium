"""Lock: a regression target is a value, not a class index (TODO90 B6c).

``synthetic_forecast`` has one continuous output and float targets ``[B, 1]``.
Three mechanisms assumed class indices and made the timeseries domain
untrainable:

- ``_align_target_rows`` folded any target whose element count matched the
  logits' row count — for ``[B, 1]`` floats that is ``[B]``, a scatter index;
- ``nudged_output`` clamped that pseudo-index at zero and scattered it
  (``scatter(): Expected dtype int32/int64 for index``);
- the pipeline computed cross-entropy and could not receive the task's own
  loss, so a regression cell optimized the wrong objective (and the trainer
  validated with it).

Each test fails if its mechanism is removed.
"""

from __future__ import annotations

import pytest
import torch
from torch import nn

from computronium import (
    AdamUpdate,
    CreditAssignmentConfig,
    DigitalSubstrate,
    GeometryConfig,
    InstantaneousDynamics,
    ParameterUpdateConfig,
    StateDynamicsConfig,
    SubstrateConfig,
    SystemState,
    compose_system,
)
from computronium.core.pipeline import _task_loss_tensor, run_train_step
from computronium.experiment.kernel.compose import compose_configs
from computronium.experiment.schema.coordinate import Coordinate
from computronium.experiment.schema.run_spec import RunSpec
from computronium.experiment.schema.seed_registries import seed_all_registries
from computronium.experiment.wave import _make_positive_control_cells
from computronium.ontology._settle_kernel import nudged_output
from computronium.ontology._utils import _align_target_rows
from computronium.ontology.credit import GradientCredit, Phase
from computronium.ontology.geometry import geometry_from_config

B, T, D = 8, 4, 16


def _regression_system():
    torch.manual_seed(0)
    return compose_system(
        substrate=DigitalSubstrate(SubstrateConfig.digital(device="cpu")),
        geometry=geometry_from_config(
            GeometryConfig.feedforward(input_dim=T, output_dim=1, hidden_dims=(8,))
        ),
        dynamics=InstantaneousDynamics(StateDynamicsConfig.instantaneous()),
        credit=GradientCredit(CreditAssignmentConfig.gradient()),
        update=AdamUpdate(ParameterUpdateConfig.adam(step_size=1e-3)),
        loss_fn=nn.MSELoss(),
    )


def test_align_target_rows_keeps_float_regression_targets() -> None:
    """A ``[B, 1]`` float target must not fold into a ``[B]`` index vector."""
    logits = torch.zeros(B, 1)
    target = torch.linspace(-1.0, 1.0, B).unsqueeze(1)
    assert _align_target_rows(logits, target).shape == (B, 1)


def test_align_target_rows_still_folds_folded_token_targets() -> None:
    """The LM fold is unchanged: integer ``[B, T]`` tokens fold to ``[B*T]``."""
    logits = torch.zeros(B * T, 5)
    target = torch.randint(0, 5, (B, T))
    assert _align_target_rows(logits, target).shape == (B * T,)


def test_nudged_output_nudges_a_float_target_without_scattering() -> None:
    out = torch.zeros(B, 1)
    target = torch.ones(B, 1)
    nudged = nudged_output(out, target, beta=0.5)
    assert torch.allclose(nudged, torch.full((B, 1), 0.5))

    # A sequence-shaped float target of the logits' element count reshapes.
    flat_target = torch.ones(B * 1, 1)
    assert nudged_output(out, flat_target, beta=0.5).shape == (B, 1)


def test_task_loss_uses_the_declared_loss_on_float_targets() -> None:
    """The declared MSE is the loss; the CE fallback cannot express the target."""
    state = SystemState(x=torch.zeros(B, T), y=torch.zeros(B, 1))
    state.activations = [torch.zeros(B, 1)]
    state.metrics = {}
    target = torch.ones(B, 1)

    with_mse, _ = _task_loss_tensor(state, target, nn.MSELoss())
    assert torch.isclose(with_mse, torch.tensor(1.0))
    with pytest.raises((IndexError, RuntimeError)):
        _task_loss_tensor(state, target, None)


def test_pipeline_trains_a_regression_cell_with_its_own_loss() -> None:
    """One real step: finite metrics, and ``free_loss`` is the task's MSE."""
    system = _regression_system()
    torch.manual_seed(0)
    x = torch.randn(B, T)
    y = torch.randn(B, 1)

    metrics = run_train_step(
        system.substrate,
        system.geometry,
        system.dynamics,
        system.credit,
        system.update,
        x,
        y,
        loss_fn=system.loss_fn,
    )

    assert torch.isfinite(torch.tensor(metrics["loss"]))
    free_prediction = system.forward(x)
    expected = torch.nn.functional.mse_loss(free_prediction, y).item()
    assert metrics["free_loss"] == pytest.approx(expected, rel=1e-5, abs=1e-6)


def test_positive_control_ladder_falls_back_from_an_illegal_hint() -> None:
    """``synthetic_forecast`` has a recurrent hint the credit rule refuses.

    The ladder must name a second arm that composes — a control the task
    cannot carry is not a control.
    """
    seed_all_registries()
    spec = RunSpec(
        task="synthetic_forecast",
        objectives=("validation_loss",),
        fidelity="L0",
        budget_seconds=60.0,
    )
    arms = _make_positive_control_cells(spec)
    assert [arm[0].geometry for arm in arms] == ["recurrent", "feedforward"]
    assert arms[0][1].epochs == 1

    def composes(geometry: str) -> bool:
        coordinate = Coordinate(
            substrate="digital",
            geometry=geometry,
            dynamics="instantaneous",
            plasticity="null",
            credit="gradient",
            update="euclidean",
            params={},
        )
        try:
            compose_configs(
                coordinate=coordinate,
                geometry={},
                input_shape=(T,),
                output_dim=1,
                param_budget=0,
                task=None,
            )
        except ValueError:
            return False
        return True

    assert not composes("recurrent")
    assert composes("feedforward")


# ---------------------------------------------------------------------------
# The regression lane of the class-readout laws (TODO91 §8, 2026-11-14)
# ---------------------------------------------------------------------------


def _regression_geometry():
    torch.manual_seed(0)
    return geometry_from_config(
        GeometryConfig.feedforward(input_dim=T, output_dim=1, hidden_dims=(8,))
    )


def test_pepita_regression_gradient_is_the_mse_gradient_at_zero_feedback() -> None:
    """γ=0 leaves the input unmodulated, so the second pass *is* the BP step.

    This is the finite-check the regression lane needs: the generalized
    branch must produce the declared MSE gradient, not merely run.
    """
    from computronium.ontology.credit import PepitaCredit

    torch.manual_seed(0)
    geometry = _regression_geometry()
    x = torch.randn(B, T)
    y = torch.randn(B, 1)
    credit = PepitaCredit(CreditAssignmentConfig.pepita(gamma=0.0, grad_clip=0.0))
    grads = credit.compute_pseudo_gradient(
        {Phase.FREE: SystemState(x=x, y=y)}, None, geometry
    )

    from computronium.ontology._utils import _learnable_weight_names

    params = [geometry.params[n] for n in _learnable_weight_names(geometry.params)]
    logits = geometry.forward(x, credit._resolved_substrate())
    expected = torch.autograd.grad(torch.nn.functional.mse_loss(logits, y), params)
    assert any(torch.count_nonzero(g) for g in grads), "the lane emitted only zeros"
    for observed, reference in zip(grads, expected, strict=True):
        assert torch.allclose(observed, reference, atol=1e-6)


def test_target_inversion_regression_target_is_the_value() -> None:
    """t_L = y for a continuous target; the propagation map is unchanged."""
    from computronium.ontology.credit import TargetInversionCredit

    torch.manual_seed(0)
    geometry = _regression_geometry()
    x = torch.randn(B, T)
    y = torch.randn(B, 1)
    acts = list(geometry.forward_with_intermediates(x, DigitalSubstrate()))
    state = SystemState(x=x, y=y)
    state.activations = acts
    credit = TargetInversionCredit(CreditAssignmentConfig.target_inversion())
    grads = credit.compute_pseudo_gradient({Phase.NUDGED: state}, None, geometry)

    from computronium.ontology._utils import _learnable_weight_names

    names = _learnable_weight_names(geometry.params)
    hidden, out = acts[1], acts[2]
    expected_hidden = (hidden - y @ geometry.params[names[1]]).T @ x / B
    expected_readout = (out - y).T @ hidden / B
    assert torch.allclose(grads[0], expected_hidden, atol=1e-6)
    assert torch.allclose(grads[1], expected_readout, atol=1e-6)


def test_class_only_primitives_are_refused_on_a_continuous_task() -> None:
    """The declared space refuses the pair instead of failing at runtime."""
    from computronium.experiment.kernel.search_space import TARGET_LANE_RULE
    from computronium.experiment.surface.combinations import declared_space

    keys = (
        "credit=local_contrastive",
        "plasticity=temporal_psi",
        "plasticity=conflict_adaptive",
    )
    seed_all_registries()
    for task in ("diabetes", "lorenz_state"):
        space = declared_space(task)
        refused = dict(space.refused)
        for key in keys:
            assert key not in space.reached, f"{task} still reaches {key}"
            assert TARGET_LANE_RULE in refused[key]

    classification = declared_space("iris")
    for key in keys:
        assert key in classification.reached, f"iris lost {key}"


def test_void_cache_is_scoped_to_the_task() -> None:
    """A task-conditional refusal must not poison the same cell for another task."""
    from computronium.experiment.kernel.search_space import VoidCache

    coordinate = Coordinate(
        substrate="digital",
        geometry="feedforward",
        dynamics="instantaneous",
        plasticity="null",
        credit="local_contrastive",
        update="adam",
        params={},
    )
    cache = VoidCache()
    cache.record_void(coordinate, "diabetes")
    assert cache.is_known_void(coordinate, "diabetes")
    assert not cache.is_known_void(coordinate, "iris")


def test_target_kind_is_joined_from_the_loss_inventory() -> None:
    """``TaskShape.target_kind`` is the loss row's target, not a second table."""
    from computronium.core.losses import LOSS_INVENTORY
    from computronium.experiment.kernel.evaluate import task_shape
    from computronium.experiment.schema.axis import AXES_REGISTRIES, StructuralAxis

    seed_all_registries()
    assert task_shape("diabetes").target_kind == "continuous"
    assert task_shape("lorenz_state").target_kind == "continuous"
    assert task_shape("iris").target_kind == "class_index"

    class_only = {
        (spec.axis_kind.value, spec.name)
        for axis in StructuralAxis
        for spec in AXES_REGISTRIES[axis]
        if spec.target_kind == "class_index"
    }
    from computronium.experiment.schema.seed_registries import CLASS_TARGET_ONLY

    # The declared table is the one source; the axis rows are its projection.
    assert class_only == {(axis.value, name) for axis, name in CLASS_TARGET_ONLY}
    assert all(
        LOSS_INVENTORY[kind].target in {"class_index", "continuous"}
        for kind in LOSS_INVENTORY
    )
