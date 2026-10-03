"""Lab train/compare — quick training, determinism, report."""

from __future__ import annotations

import pytest
import torch
from computronium_lab import Lab
from computronium.core.system_trainer import compose_joint_system
from computronium.ontology import (
    DigitalSubstrate,
    EnergyMinimizationDynamics,
    EuclideanUpdate,
    GeometryConfig,
    NullPlasticity,
    RecurrentGeometry,
    StateDynamicsConfig,
    SubstrateConfig,
    ThermodynamicContrast,
)


def _make_backprop_mlp(input_dim: int = 32, output_dim: int = 4) -> object:
    """Compose a backprop MLP system."""
    return compose_joint_system(
        substrate=DigitalSubstrate(SubstrateConfig.digital(device="cpu")),
        geometry=RecurrentGeometry(
            GeometryConfig.recurrent(input_dim=input_dim, output_dim=output_dim, hidden_dims=(64,))
        ),
        dynamics=EnergyMinimizationDynamics(StateDynamicsConfig.energy_minimization(max_steps=5)),
        plasticity=NullPlasticity(),
        credit=ThermodynamicContrast(),
        update=EuclideanUpdate(),
    )


def test_train_returns_finite_metrics() -> None:
    lab = Lab(seed=0)
    system = _make_backprop_mlp()
    result = lab.train(system, epochs=1)
    assert result.metrics["loss"] > 0.0
    assert 0.0 <= result.metrics["accuracy"] <= 1.0
    assert result.walltime_s > 0.0


def test_train_unknown_task_rejected() -> None:
    lab = Lab()
    system = _make_backprop_mlp()
    with pytest.raises(ValueError, match="task"):
        lab.train(system, task="digits")


def test_compare_runs_multiple_systems() -> None:
    """Compare runs multiple systems and returns results for each."""
    systems = [("mlp1", _make_backprop_mlp()), ("mlp2", _make_backprop_mlp())]
    results = Lab(seed=0).compare(systems, epochs=1)
    assert len(results) == 2
    for r in results:
        assert 0.0 <= r.final_accuracy <= 1.0
        assert r.final_loss > 0.0


def test_compare_backprop_beats_chance_at_five_epochs() -> None:
    results = Lab(seed=0).compare([("backprop_mlp", _make_backprop_mlp())], epochs=5)
    assert results[0].final_accuracy > 0.3  # chance is 0.25 at (1.2, 1.5)


def test_report_writes_markdown(tmp_path) -> None:
    lab = Lab(seed=0)
    lab.compare([("backprop_mlp", _make_backprop_mlp())], epochs=1)
    path = tmp_path / "report.md"
    content = lab.report(str(path))
    assert path.exists()
    assert "backprop_mlp" in content
    assert content.startswith("# Computronium Lab comparison")
    with pytest.raises(ValueError, match="nothing to report"):
        Lab().report(str(tmp_path / "empty.md"))


def test_train_data_passthrough(tmp_path) -> None:
    """Explicit train_data bypasses the synthetic task (TODO25 F1)."""
    from torch.utils.data import DataLoader, TensorDataset

    loader = DataLoader(
        TensorDataset(torch.randn(16, 8), torch.randint(0, 2, (16,))),
        batch_size=8,
    )
    lab = Lab(seed=0)
    system = _make_backprop_mlp(input_dim=8, output_dim=2)
    result = lab.train(system, epochs=1, train_data=loader)
    assert result.metrics["loss"] > 0.0