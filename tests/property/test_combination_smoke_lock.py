"""Lock: the legal-coordinate smoke trains, and its refusals name a rule (S6).

TODO91 S6's claim is that every combination the declared rules admit can
compose and train. This lock protects that claim from both directions:

- a **budget-8 cover** must train 8 admitted cells with zero failures — so a
  regression in compose/trainer/credit turns the lock red instead of surfacing
  as a silent FAIL cell in a later run;
- the **planner** must cover every reachable coordinate at an uncapped budget,
  asserted at the coordinate level (planning only, no training), so a widening
  or narrowing of the declared space is visible;
- a coordinate no cell can hold must carry the rule that refuses it, and the
  measured shape rules must refuse the cell that used to die in training.

Each test fails if its mechanism is removed: delete a declared constraint and
the cover admits a cell that cannot train; delete the shape rule and conv
reaches a flat input; delete the readout-replacing declaration and the gradient
credit dies on an unused projection.
"""

from __future__ import annotations

import pytest

from computronium.core.plasticity import (
    READOUT_REPLACING_PLASTICITIES,
    ConflictAdaptivePsiConfig,
)
from computronium.experiment.schema.seed_registries import seed_all_registries
from computronium.experiment.surface.combinations import (
    declared_space,
    plan_cover,
    run_combinations,
)

TASKS = ("iris", "mnist", "cora")


@pytest.fixture(scope="module", autouse=True)
def _registries() -> None:
    seed_all_registries()


@pytest.mark.timeout(300)
def test_budget_eight_cover_trains_with_zero_failures() -> None:
    """A budget-8 cover must admit 8 cells and train every one."""
    report = run_combinations(TASKS, budget=8, seed=0)
    assert len(report.results) == 8
    assert report.failures == (), report.render()


@pytest.mark.timeout(300)
def test_planner_covers_every_reachable_coordinate() -> None:
    """At an uncapped budget the cover reaches every coordinate some task holds."""
    spaces = tuple(declared_space(task) for task in TASKS)
    cover = plan_cover(spaces, seed=0, budget=None)
    covered = {key for cell in cover for key in cell.covers}
    reachable = set().union(*(space.reached for space in spaces))
    assert reachable <= covered
    # 60 runtime coordinates; the complex substrate is declared unreachable.
    assert len(reachable) == 60


def test_unreachable_coordinate_names_its_rule() -> None:
    """``substrate=complex`` is refused by the rule that voids it, not by luck."""
    space = declared_space("iris")
    refused = dict(space.refused)
    assert "substrate=complex" in refused
    assert "complex_substrate_real_compute" in refused["substrate=complex"]


def test_shape_rule_refuses_the_measured_failures() -> None:
    """conv needs a grid; the causal transformer needs patches or token labels."""
    from computronium.experiment.kernel.evaluate import task_shape
    from computronium.experiment.kernel.search_space import (
        _is_geometry_task_compatible,
    )

    iris = task_shape("iris", "cpu")
    mnist = task_shape("mnist", "cpu")
    cora = task_shape("cora", "cpu")
    assert not _is_geometry_task_compatible("conv", iris, "iris")
    assert _is_geometry_task_compatible("conv", mnist, "mnist")
    assert not _is_geometry_task_compatible("causal_transformer", iris, "iris")
    assert _is_geometry_task_compatible("causal_transformer", mnist, "mnist")
    assert not _is_geometry_task_compatible("graph", iris, "iris")
    assert _is_geometry_task_compatible("graph", cora, "cora")


def test_declared_nonlayered_rule_is_the_runtime_set() -> None:
    """The registry's non-layered rule and ``SystemConfig`` share one table."""
    from computronium.experiment.kernel.search_space import _compiled_void_constraints
    from computronium.ontology.system import (
        NONLAYERED_GEOMETRIES,
        SETTLING_DYNAMICS,
    )

    indep, _dep = _compiled_void_constraints()
    rule = dict(indep)["nonlayered_geometry_dynamics"]
    for geometry in NONLAYERED_GEOMETRIES:
        for dynamics in SETTLING_DYNAMICS:
            values = ("digital", geometry, dynamics, "null", "gradient", "adam", "")
            assert not rule(values), (geometry, dynamics)
        instant = ("digital", geometry, "instantaneous", "null", "gradient", "adam", "")
        assert rule(instant), geometry
    # graph settles (measured): it is not in the non-layered table.
    assert "graph" not in NONLAYERED_GEOMETRIES
    graph = ("digital", "graph", "energy_minimization", "null", "gradient", "adam", "")
    assert rule(graph)


def test_readout_replacing_plasticity_defaults_agree_with_the_declaration() -> None:
    """The declared tuple names plasticities whose config replaces the readout."""
    assert "conflict_adaptive" in READOUT_REPLACING_PLASTICITIES
    assert ConflictAdaptivePsiConfig().replace_readout is True
