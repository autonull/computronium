"""Dry-run gate lock (TODO57 D2).

The search space must reject coordinates that would fail at training time
due to detached settle graphs, FA contract failures, or no-gradient-reached.
Removing the gate must make the fixture fail (TODO46 D25).
"""

from __future__ import annotations

from computronium.experiment.execution.compose import compose_cell_system
from computronium.experiment.execution.evaluate import task_shape
from computronium.experiment.execution.search_space import _composable
from computronium.experiment.schema import Coordinate


def test_random_projections_rejects_nca_digits() -> None:
    """random_projections + nca on digits must be rejected by dry-run."""
    coord = Coordinate(
        substrate="digital",
        geometry="nca",
        dynamics="instantaneous",
        plasticity="null",
        credit="random_projections",
        update="adam",
        params={},
    )
    result = _composable(coord, "digits", task_shape, 50000)
    assert result is False, "random_projections + nca must be rejected for digits"


def test_random_projections_accepts_feedforward_digits() -> None:
    """random_projections + feedforward on digits must be accepted."""
    coord = Coordinate(
        substrate="digital",
        geometry="feedforward",
        dynamics="instantaneous",
        plasticity="null",
        credit="random_projections",
        update="adam",
        params={},
    )
    result = _composable(coord, "digits", task_shape, 50000)
    assert result is True, (
        "random_projections + feedforward must be accepted for digits"
    )


def test_gradient_accepts_feedforward_digits() -> None:
    """gradient + feedforward on digits must be accepted."""
    coord = Coordinate(
        substrate="digital",
        geometry="feedforward",
        dynamics="instantaneous",
        plasticity="null",
        credit="gradient",
        update="adam",
        params={},
    )
    result = _composable(coord, "digits", task_shape, 50000)
    assert result is True, "gradient + feedforward must be accepted for digits"


def test_compose_dry_run_catches_failure() -> None:
    """Direct compose + dry-run must catch the failure."""
    coord = Coordinate(
        substrate="digital",
        geometry="nca",
        dynamics="instantaneous",
        plasticity="null",
        credit="random_projections",
        update="adam",
        params={},
    )
    shape = task_shape("digits")
    # compose_cell_system should succeed (it doesn't run dry-run)
    cell = compose_cell_system(
        coordinate=coord,
        geometry={},
        input_shape=shape.input_shape,
        output_dim=shape.output_dim,
        param_budget=50000,
    )
    assert cell is not None

    # But the dry-run function should catch it
    from computronium.experiment.execution.compose import _dry_run_trainable

    ok, reason = _dry_run_trainable(
        coord, {}, shape.input_shape, shape.output_dim, 50000
    )
    assert ok is False
    assert "all-zero pseudo-gradient" in reason or "layered FA contract" in reason


def test_gate_removal_regression() -> None:
    """If the dry-run gate is removed, the fixture must fail.

    This test verifies the lock is not a comment (TODO46 D25).
    """
    from computronium.experiment.execution import compose as compose_module
    from computronium.experiment.execution import search_space as search_space_module

    # Save original
    original_dry_run = compose_module._dry_run_trainable

    def always_pass(*args, **kwargs):
        return True, "bypassed"

    try:
        compose_module._dry_run_trainable = always_pass
        # Clear the cache so the patched function is called
        search_space_module._composable_cache.clear()
        coord = Coordinate(
            substrate="digital",
            geometry="nca",
            dynamics="instantaneous",
            plasticity="null",
            credit="random_projections",
            update="adam",
            params={},
        )
        result = _composable(coord, "digits", task_shape, 50000)
        # Without the gate, this would be accepted (which is the bug)
        assert result is True, (
            "Lock broken: removing dry-run gate must make nca+random_projections pass for digits"
        )
    finally:
        compose_module._dry_run_trainable = original_dry_run


def test_known_bad_coordinate_rejected() -> None:
    """A known-bad coordinate (conv + random_projections) must be rejected."""
    # conv geometry with random_projections credit often has width mismatch
    coord = Coordinate(
        substrate="digital",
        geometry="conv",
        dynamics="instantaneous",
        plasticity="null",
        credit="random_projections",
        update="adam",
        params={},
    )
    result = _composable(coord, "digits", task_shape, 50000)
    # This should be rejected due to width mismatch in FA contract
    assert result is False, "conv + random_projections must be rejected for digits"
