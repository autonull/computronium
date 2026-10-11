"""Lock: default ``production-map`` sampling must yield legal, diverse cells.

Regression this guards: the walk was a row-major Cartesian sweep whose slowest
axis (geometry) locked onto the non-layered values while dynamics cycled, so the
first ~124,000 candidates were all illegal. ``iter_candidates`` therefore yielded
zero cells, the runner burned its entire budget scanning, and report generation
crashed on an empty store. The fix is a golden-spaced affine permutation over the
mixed-radix index, which samples every axis at once.

These tests use the *real* profile with *empty* axes — the path that was never
exercised. Toy axes always yielded cells and hid the defect.
"""

from __future__ import annotations

import pytest

from computronium.experiment.execution.evaluate import task_shape
from computronium.experiment.execution.search_space import (
    declared_cell_count,
    iter_candidates,
    search_space_from_spec,
)
from computronium.experiment.schema import RunSpec
from computronium.experiment.surface.cli import RUN_PROFILES


def _production_map_spec(seed: int = 42) -> RunSpec:
    profile = RUN_PROFILES["production-map"]
    return RunSpec(
        profile=profile.name,
        task=profile.task,
        objectives=profile.objectives,
        stages=tuple(profile.stages),
        fidelity=profile.fidelity,
        n_seeds=profile.n_seeds,
        epochs=profile.epochs,
        batch_limit=profile.batch_limit,
        budget_seconds=3600.0,
        param_budget=profile.param_budget,
        policy="round_robin_grid",
        axes=profile.axes,
        checkpoint_every_n=profile.checkpoint_every_n,
        seed=seed,
        device="cpu",
    )


def _sample(spec: RunSpec, max_scan: int) -> list:
    space = search_space_from_spec(spec, tasks=spec.task_names)
    return list(
        iter_candidates(
            spec, space, shape=task_shape, check_composable=True, max_scan=max_scan
        )
    )


def test_production_map_declares_full_space():
    spec = _production_map_spec()
    space = search_space_from_spec(spec, tasks=spec.task_names)
    assert declared_cell_count(spec, space) > 1_000_000


def test_first_legal_cell_appears_promptly():
    """A legal cell must appear within the first handful of candidates.

    The pre-fix sweep placed the first legal cell at scan index ~124,290; a
    ``max_scan`` of 50 fails loudly if corner-first ordering ever returns.
    """
    cells = _sample(_production_map_spec(), max_scan=50)
    assert cells, "no legal cell in the first 50 candidates of production-map"


@pytest.mark.timeout(300)
def test_prefix_is_diverse():
    """The leading sample must span the ontology, not a corner of it."""
    cells = _sample(_production_map_spec(), max_scan=600)
    substrates = {c.substrate for c, _ in cells}
    geometries = {c.geometry for c, _ in cells}
    dynamics = {c.dynamics for c, _ in cells}
    assert len(substrates) >= 8, f"substrates covered: {sorted(substrates)}"
    assert len(geometries) >= 5, f"geometries covered: {sorted(geometries)}"
    assert len(dynamics) >= 3, f"dynamics covered: {sorted(dynamics)}"


@pytest.mark.timeout(300)
def test_walk_is_deterministic_per_seed():
    """Same seed reproduces the same order; the traversal stays reproducible."""
    first = _sample(_production_map_spec(seed=42), max_scan=300)
    second = _sample(_production_map_spec(seed=42), max_scan=300)
    keys_a = [(c.measurement_key(s), c.cell_key()) for c, s in first]
    keys_b = [(c.measurement_key(s), c.cell_key()) for c, s in second]
    assert keys_a == keys_b
