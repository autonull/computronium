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
from computronium.ontology.credit import GradientCredit
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
