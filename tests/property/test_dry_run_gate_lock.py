"""Dry-run gate lock (TODO57 D2, declaration in TODO89 T7).

The search space must reject coordinates that would fail at training time
due to detached settle graphs, FA contract failures, or no-gradient-reached.
Measured all-zero geometries are declared void; the dry-run probe stays as the
runtime backstop for any geometry the declaration does not name. Removing
either mechanism must make a fixture fail (TODO46 D25).
"""

from __future__ import annotations

import pytest

from computronium.experiment.kernel.compose import compose_cell_system
from computronium.experiment.kernel.evaluate import task_shape
from computronium.experiment.kernel.search_space import _composable
from computronium.experiment.schema import Coordinate


def _nca_random_projections() -> Coordinate:
    return Coordinate(
        substrate="digital",
        geometry="nca",
        dynamics="instantaneous",
        plasticity="null",
        credit="random_projections",
        update="adam",
        params={},
    )


def _nca_target_inversion() -> Coordinate:
    coordinate = _nca_random_projections().to_dict()
    coordinate["credit"] = "target_inversion"
    return Coordinate(**coordinate)


def _declared_reason(coordinate: Coordinate) -> str | None:
    """The first declared void constraint this coordinate violates."""
    from computronium.experiment.kernel import search_space

    indep, dep = search_space._compiled_void_constraints()
    return search_space._structural_rejection(
        coordinate, "digits", indep, dep, void_cache=None, rejections=None
    )


def test_random_projections_accepts_nca_digits() -> None:
    """random_projections + nca on digits must pass (cell-mode FA readout)."""
    result = _composable(_nca_random_projections(), "digits", task_shape, 50000)
    assert result is True, "random_projections + nca must be accepted for digits"


def test_target_inversion_accepts_nca_digits() -> None:
    """target_inversion + nca on digits must pass (cell-fold target propagation).

    The declaration that voided this coordinate is deleted; the dry-run probe
    is the backstop, so a broken fold would still refuse the cell.
    """
    coordinate = _nca_target_inversion()
    assert _declared_reason(coordinate) is None
    result = _composable(coordinate, "digits", task_shape, 50000)
    assert result is True, "target_inversion + nca must be accepted for digits"


@pytest.mark.parametrize("geometry", ["attention", "spatial_lattice", "conv", "ntm"])
def test_feedback_alignment_geometries_are_declared_void(geometry: str) -> None:
    """The measured all-zero geometries are declared, not inferred by dry-run.

    Each coordinate's refusal must name the declaration. Deleting the row (or
    one geometry from its list) makes this fixture fail, so the lock contains
    the case it exists for.
    """
    coordinate = _nca_random_projections().to_dict()
    coordinate["geometry"] = geometry
    reason = _declared_reason(Coordinate(**coordinate))
    assert reason == "void constraint: random_projections_layered_geometry"


def test_declared_row_is_what_prunes_the_coordinate() -> None:
    """Bypass the dry run and drop the row: the coordinate becomes composable.

    Proves the declaration is the mechanism. Restoring the dry-run backstop
    without the row reports the all-zero layered-FA contract, so the probe
    still names the same failure for any geometry the declaration misses.
    """
    from computronium.experiment.kernel import compose as compose_module
    from computronium.experiment.kernel import search_space as search_space_module
    from computronium.experiment.schema.seed_registries import CONSTRAINTS_REGISTRY

    coordinate = _nca_random_projections().to_dict()
    coordinate["geometry"] = "conv"
    coordinate = Coordinate(**coordinate)
    spec = CONSTRAINTS_REGISTRY["random_projections_layered_geometry"]
    CONSTRAINTS_REGISTRY.unregister("random_projections_layered_geometry")
    original_dry_run = compose_module._dry_run_trainable
    try:
        assert _declared_reason(coordinate) is None

        def _always_ok(*_args: object, **_kwargs: object) -> tuple[bool, str]:
            return True, "bypassed"

        compose_module._dry_run_trainable = _always_ok  # type: ignore[assignment]
        search_space_module._composable_cache.clear()
        assert _composable(coordinate, "digits", task_shape, 50000) is True, (
            "declaration removed and dry run bypassed: the coordinate must compose"
        )
        compose_module._dry_run_trainable = original_dry_run
        search_space_module._composable_cache.clear()
        assert _composable(coordinate, "digits", task_shape, 50000) is False
    finally:
        compose_module._dry_run_trainable = original_dry_run
        CONSTRAINTS_REGISTRY.register(spec)
        search_space_module._composable_cache.clear()


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
        geometry="conv",
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
    from computronium.experiment.kernel.compose import _dry_run_trainable

    ok, reason = _dry_run_trainable(
        coord, {}, shape.input_shape, shape.output_dim, 50000
    )
    assert ok is False
    assert "all-zero pseudo-gradient" in reason or "layered FA contract" in reason


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
