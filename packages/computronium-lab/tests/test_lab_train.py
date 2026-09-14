"""Lab train/compare — quick training, determinism, report."""

from __future__ import annotations

import pytest
import torch
from computronium_lab import Lab


def test_train_returns_finite_metrics() -> None:
    lab = Lab(seed=0)
    system = lab.compose("backprop_mlp")
    result = lab.train(system, epochs=1)
    assert result.metrics["loss"] > 0.0
    assert 0.0 <= result.metrics["accuracy"] <= 1.0
    assert result.walltime_s > 0.0


def test_train_unknown_task_rejected() -> None:
    lab = Lab()
    system = lab.compose("backprop_mlp")
    with pytest.raises(ValueError, match="task"):
        lab.train(system, task="mnist")


def test_compare_is_order_and_run_deterministic() -> None:
    names = ["backprop_mlp", "fa_mlp"]
    forward = Lab(seed=0).compare(names, epochs=1)
    backward = Lab(seed=0).compare(list(reversed(names)), epochs=1)
    by_name_f = {r.preset: r for r in forward}
    by_name_b = {r.preset: r for r in backward}
    for name in names:
        assert by_name_f[name].final_accuracy == by_name_b[name].final_accuracy
        assert by_name_f[name].final_loss == by_name_b[name].final_loss


def test_compare_backprop_beats_chance_at_five_epochs() -> None:
    results = Lab(seed=0).compare(["backprop_mlp"], epochs=5)
    assert results[0].final_accuracy > 0.3  # chance is 0.25 at (1.2, 1.5)


def test_report_writes_markdown(tmp_path) -> None:
    lab = Lab(seed=0)
    lab.compare(["backprop_mlp"], epochs=1)
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
    system = lab.compose("backprop_mlp", input_dim=8, output_dim=2)
    result = lab.train(system, epochs=1, train_data=loader)
    assert result.metrics["loss"] > 0.0
