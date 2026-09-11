"""Lab train/compare — quick training, determinism, report."""

from __future__ import annotations

import pytest
from computronium_lab import Lab


def test_train_returns_finite_metrics() -> None:
    lab = Lab(seed=0)
    system = lab.compose("backprop_mlp")
    metrics = lab.train(system, epochs=1)
    assert metrics["loss"] > 0.0
    assert 0.0 <= metrics["accuracy"] <= 1.0


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
    assert results[0].final_accuracy > 0.6


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
