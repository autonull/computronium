"""Tests for SimpleSurvey - dry-run driven development."""

from __future__ import annotations

import pytest

from computronium.experiment import simple_survey
from computronium.experiment.execution.pipeline._admission_gate import (
    check_compose_gate,
)
from computronium.experiment.simple_survey import run_simple_survey


def test_dry_run_generates_valid_cells():
    """Dry-run should generate valid cells that pass compatibility checks."""
    result = run_simple_survey(
        0.01,
        fidelity="L0",
        dry_run=True,
    )
    assert result["n"] > 0
    assert len(result["cells"]) == result["n"]

    for coord, sched in result["cells"]:
        passed, message = check_compose_gate(coord, sched)
        assert passed, f"Invalid coordinate: {message}"


def test_dry_run_fidelity_l0():
    """L0 fidelity should use cheap tasks."""
    result = run_simple_survey(0.01, fidelity="L0", dry_run=True)
    assert result["fidelity"] == "L0"
    assert result["n"] > 0
    # Should have tasks
    assert len(result["tasks"]) > 0


def test_dry_run_fidelity_l1():
    """L1 fidelity should use cheap + medium tasks."""
    result = run_simple_survey(0.01, fidelity="L1", dry_run=True)
    assert result["fidelity"] == "L1"
    assert result["n"] > 0
    # Should have more tasks than L0
    assert len(result["tasks"]) > 0


def test_dry_run_fidelity_l2():
    """L2 fidelity should use all tasks."""
    result = run_simple_survey(0.01, fidelity="L2", dry_run=True)
    assert result["fidelity"] == "L2"
    assert result["n"] > 0
    # Should have most tasks
    assert len(result["tasks"]) > 0


def test_dry_run_custom_tasks():
    """Custom task list should be respected."""
    result = run_simple_survey(
        0.01,
        fidelity="L0",
        tasks=["xor", "spiral"],
        dry_run=True,
    )
    assert set(result["tasks"]) == {"xor", "spiral"}


def test_dry_run_axes_selection():
    """Axis selection should restrict primitives."""
    allowed_dynamics = {"energy_minimization", "instantaneous"}
    result = run_simple_survey(
        0.01,
        fidelity="L0",
        axes={"dynamics": ("energy_minimization", "instantaneous")},
        dry_run=True,
    )
    assert result["n"] > 0
    for coord, _ in result["cells"]:
        assert coord.dynamics in allowed_dynamics


def test_dry_run_reproducible_with_seed():
    """Same seed should produce same cells."""
    result1 = run_simple_survey(0.01, fidelity="L0", seed=42, dry_run=True)
    result2 = run_simple_survey(0.01, fidelity="L0", seed=42, dry_run=True)

    assert result1["n"] == result2["n"]
    for (c1, _), (c2, _) in zip(result1["cells"], result2["cells"]):
        assert c1.cell_key() == c2.cell_key()


def test_dry_run_different_seeds_produce_different_cells():
    """Different seeds should produce different cells."""
    result1 = run_simple_survey(0.01, fidelity="L0", seed=42, dry_run=True)
    result2 = run_simple_survey(0.01, fidelity="L0", seed=123, dry_run=True)

    # At least some cells should differ
    keys1 = {c.cell_key() for c, _ in result1["cells"]}
    keys2 = {c.cell_key() for c, _ in result2["cells"]}
    assert keys1 != keys2


def test_compatibility_filtering():
    """Every generated cell composes for its task shape."""
    result = run_simple_survey(0.01, fidelity="L0", dry_run=True)

    for coord, sched in result["cells"]:
        passed, message = check_compose_gate(coord, sched)
        assert passed, f"Found violations: {message}"


def test_cell_count_scales_with_budget():
    """Cell count should scale with time budget."""
    result_small = run_simple_survey(0.01, fidelity="L0", dry_run=True)
    result_large = run_simple_survey(0.1, fidelity="L0", dry_run=True)

    assert result_large["n"] >= result_small["n"]


def test_promote_from_dry_run():
    """Promote-from should work in dry-run mode (even without prior store)."""
    # This should not crash even if the store doesn't exist
    result = run_simple_survey(
        0.01,
        fidelity="L1",
        promote_from="nonexistent.duckdb",
        promote_top=5,
        dry_run=True,
    )
    # Should fall back to random exploration
    assert result["n"] > 0


def test_estimate_cell_count_from_budget():
    """Cell count is budget minus startup, divided by the per-cell cost."""
    model = simple_survey.CostModel(cost_per_cell_s=10.0, startup_s=10.0)

    assert simple_survey._estimate_cell_count(50, model) == 4


def test_estimate_cell_count_never_zero():
    """A budget smaller than startup still runs one cell."""
    model = simple_survey.CostModel(cost_per_cell_s=10.0, startup_s=10.0)

    assert simple_survey._estimate_cell_count(1, model) == 1


def test_cost_model_round_trip(tmp_path, monkeypatch):
    """A measurement survives to the next run through the cache."""
    from computronium.experiment import wave

    monkeypatch.setattr(wave, "TIMING_CACHE", tmp_path / ".timing.json")
    measured = wave.CostModel(9.25, 5.5, measured=True)

    wave._save_cost_model("cpu", "L0", measured)
    loaded = wave._load_cost_model("cpu", "L0")

    assert loaded.measured is True
    assert loaded.cost_per_cell_s == pytest.approx(9.25)
    assert loaded.startup_s == pytest.approx(5.5)


def test_cost_model_missing_falls_back_to_defaults(tmp_path, monkeypatch):
    """No cache entry means the documented fallback table, not a crash."""
    from computronium.experiment import wave

    monkeypatch.setattr(wave, "TIMING_CACHE", tmp_path / "absent.json")

    model = wave._load_cost_model("cpu", "L0")

    assert model.measured is False
    assert model.cost_per_cell_s == wave.DEFAULT_COSTS["L0"]
    assert model.startup_s == wave.DEFAULT_STARTUP_S


def test_digital_flag_pins_substrate():
    """--digital restricts the substrate axis and keeps other axes intact."""
    from computronium.experiment import wave

    axes = wave._axis_overrides('{"dynamics": ["lazy"]}', digital=True)

    assert axes == {"dynamics": ["lazy"], "substrate": ("digital",)}

    result = run_simple_survey(0.01, fidelity="L0", axes=axes, dry_run=True)
    assert result["n"] > 0
    assert {coord.substrate for coord, _ in result["cells"]} == {"digital"}


def test_axis_overrides_without_digital_is_passthrough():
    """Without --digital the JSON is used as written."""
    from computronium.experiment import wave

    assert wave._axis_overrides("", digital=False) is None
    assert wave._axis_overrides('{"dynamics": ["lazy"]}', digital=False) == {
        "dynamics": ["lazy"]
    }


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
