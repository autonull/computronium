"""Tests for SimpleSurvey - dry-run driven development."""

from __future__ import annotations

import pytest

from computronium.experiment.simple_survey import run_simple_survey
from computronium.ontology.system import check_compatibility_matrix


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
        violations = check_compatibility_matrix(
            coord.substrate,
            coord.geometry,
            coord.dynamics,
            coord.plasticity,
            coord.credit,
            coord.update,
        )
        assert violations == [], f"Invalid coordinate: {violations}"


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
    """Compatibility matrix should filter invalid combinations."""
    result = run_simple_survey(0.01, fidelity="L0", dry_run=True)

    # All generated cells should be compatible
    for coord, _ in result["cells"]:
        violations = check_compatibility_matrix(
            coord.substrate,
            coord.geometry,
            coord.dynamics,
            coord.plasticity,
            coord.credit,
            coord.update,
        )
        assert violations == [], f"Found violations: {violations}"


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


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
