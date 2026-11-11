"""Lock: token targets ``[B, T]`` reach the folded logits ``[B*T, V]`` (R8).

``TransformerGeometry`` folds the sequence dim into the batch, so an LM cell
produces logits ``[B*T, V]`` while ``LMTask`` returns next-token targets
``[B, T]``. The nudged phase, the task loss and validation all consume the
output, so every one of them must fold the target — otherwise LM training dies
in settle before a single weight moves. Each test fails if the fold is removed
(the old code returned the 2-D target and broadcast-failed).
"""

from __future__ import annotations

import math

import pytest
import torch

from computronium import (
    AdamUpdate,
    CreditAssignmentConfig,
    DigitalSubstrate,
    InstantaneousDynamics,
    LocalGoodnessCredit,
    ParameterUpdateConfig,
    StateDynamicsConfig,
    SubstrateConfig,
    SystemState,
    compose_system,
)
from computronium.core.pipeline import run_train_step
from computronium.ontology._settle_kernel import nudged_output
from computronium.ontology.geometry import GeometryConfig, geometry_from_config

V, T, D, H = 17, 8, 16, 2


def _geometry():
    return geometry_from_config(
        GeometryConfig.causal_transformer(
            vocab_size=V, d_model=D, n_layers=1, n_heads=H, seq_len=T
        )
    )


def _system():
    torch.manual_seed(0)
    return compose_system(
        substrate=DigitalSubstrate(SubstrateConfig.digital(device="cpu")),
        geometry=_geometry(),
        dynamics=InstantaneousDynamics(StateDynamicsConfig.instantaneous()),
        credit=LocalGoodnessCredit(
            CreditAssignmentConfig.local_goodness(
                local_objective="ff", feedback_scale=0.01
            )
        ),
        update=AdamUpdate(ParameterUpdateConfig.adam(step_size=1e-3)),
    )


def test_nudged_output_folds_token_targets() -> None:
    out = torch.randn(T * 2, V)
    y = torch.randint(0, V, (2, T))
    nudged = nudged_output(out, y, 0.5)
    onehot = torch.nn.functional.one_hot(y.reshape(-1), V).to(out.dtype)
    assert nudged.shape == out.shape
    assert torch.allclose(nudged, out + 0.5 * (onehot - out))


def test_nudged_output_keeps_ignore_index_free() -> None:
    out = torch.randn(4, V)
    y = torch.tensor([1, -100, 3, -100])
    nudged = nudged_output(out, y, 0.5)
    assert torch.equal(nudged[1], out[1])
    assert torch.equal(nudged[3], out[3])
    assert not torch.equal(nudged[0], out[0])


@pytest.mark.timeout(120)
def test_settle_accepts_sequence_targets() -> None:
    system = _system()
    ids = torch.randint(0, V, (2, T))
    y = torch.randint(0, V, (2, T))
    state = SystemState(x=ids, y=y)
    nudged = system.dynamics.settle(state, system.geometry, system.substrate, target=y)
    acts = nudged.activations
    logits = acts[-1] if isinstance(acts, list) else acts
    assert logits.shape == (2 * T, V)


@pytest.mark.timeout(120)
def test_train_step_accepts_sequence_targets() -> None:
    system = _system()
    ids = torch.randint(0, V, (2, T))
    y = torch.randint(0, V, (2, T))
    metrics = run_train_step(
        system.substrate,
        system.geometry,
        system.dynamics,
        system.credit,
        system.update,
        ids,
        y,
    )
    assert math.isfinite(metrics["loss"])


@pytest.mark.timeout(120)
def test_trainer_validate_accepts_sequence_targets() -> None:
    from computronium.core.system_trainer import SystemTrainer, SystemTrainerConfig

    gen = torch.Generator().manual_seed(1)
    data = [
        (
            torch.randint(0, V, (2, T), generator=gen),
            torch.randint(0, V, (2, T), generator=gen),
        )
        for _ in range(2)
    ]
    trainer = SystemTrainer(
        system=_system(),
        config=SystemTrainerConfig(max_epochs=1, device="cpu", seed=0),
        train_data=data,
        val_data=data,
    )
    history = trainer.fit()
    assert math.isfinite(history[-1]["val_loss"])
    assert math.isfinite(history[-1]["val_acc"])
