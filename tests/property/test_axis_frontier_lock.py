"""Lock: a Pareto front has as many axes as the run declared for them.

TODO51 §1 declares a full objective set per structural axis — six names for
stability (rho, sigma_max, nonnormality, margin, lyapunov, settle_steps), three
for cost. `ReportGenerator._pareto_subset` was hardcoded to two: it read
``payload[objectives[0]]`` and ``payload[objectives[1]]``, dropped every other
name the axis declared, and called the result a front. The stability front it
reported was a front over (rho, sigma_max) with the other four axes
unconstrained — a wider set than the one asked for, presented as the one asked
for.

Three locks:

* **arity is honoured** — a third axis that dominates must remove a point that
  a two-axis front kept;
* **directions are per axis** — minimizing rho and maximizing accuracy is the
  usual case and inverting either empties the front;
* **a missing objective removes the record** — substituting a default would
  place an unmeasured cell on the front.
"""

from __future__ import annotations

import pytest

from computronium.experiment.surface import non_dominated

_RHO, _SIGMA, _MARGIN = "spectral_radius", "max_singular_value", "stability_margin"


def _keep(vectors, axes, maximize) -> list[int]:
    return non_dominated(vectors, axes, maximize)


def test_a_third_axis_can_dominate_what_two_axes_cannot() -> None:
    """The whole point: arity is the difference between the two fronts.

    Two cells that tie on (rho, sigma_max) are indistinguishable to a two-axis
    filter, so both sit on the front. The stability axis declares four more
    names; settle_steps among them separates them, and the front narrows to one.
    A two-axis filter reports the wider set as the front the axis asked for.
    """
    vectors = [
        {_RHO: 0.90, _SIGMA: 1.05, _MARGIN: 0.10},
        {_RHO: 0.90, _SIGMA: 1.05, _MARGIN: 0.30},
    ]
    two_axis = _keep(vectors, (_RHO, _SIGMA), (False, False))
    three_axis = _keep(vectors, (_RHO, _SIGMA, _MARGIN), (False, False, True))

    assert two_axis == [0, 1], "tied on both axes, so both stay"
    assert three_axis == [1], "the margin axis breaks the tie and dominates the first"


def test_directions_are_read_per_axis() -> None:
    """Minimize rho, maximize accuracy: the pair must not invert one."""
    vectors = [
        {"validation_accuracy": 0.90, "spectral_radius": 1.10},
        {"validation_accuracy": 0.80, "spectral_radius": 0.50},
    ]
    axes = ("validation_accuracy", _RHO)

    assert _keep(vectors, axes, (True, False)) == [0, 1], "neither dominates"
    assert _keep(vectors, axes, (True, True)) == [0], "the first dominates both"


def test_arity_and_direction_counts_must_agree() -> None:
    with pytest.raises(ValueError, match="3 axes but 2 directions"):
        non_dominated([{_RHO: 1.0}], (_RHO, _SIGMA, _MARGIN), (False, False))


def test_the_axes_are_named_not_read_off_the_first_point() -> None:
    """A point carries bookkeeping fields that are not axes.

    Reading the axes off a point's keys walks ``coordinate`` and ``cell_key``
    as if they were objectives, which is an ``IndexError`` on the directions
    list and a ``KeyError`` on the values.
    """
    points = [{"rho": 0.9, "cell_key": "abc", "objectives": {"rho": 0.9}}]
    assert _keep(points, ("rho",), (False,)) == [0]


def test_a_duplicated_point_does_not_dominate_itself() -> None:
    """Ties keep every point: a front of one repeated value is the whole run."""
    vectors = [{_RHO: 0.9}, {_RHO: 0.9}, {_RHO: 1.5}]
    assert _keep(vectors, (_RHO,), (False,)) == [0, 1], (
        "the tied pair stays; the point both dominate goes"
    )


def test_stability_axis_front_is_not_a_two_axis_front() -> None:
    """The stability axis's real arity, over the shape the evaluator writes.

    A front computed over the first two names only would keep the first point
    here; over all six it does not.
    """
    stability = {
        _RHO: ("spectral_radius", False),
        _SIGMA: ("max_singular_value", False),
        "nonnormality": ("nonnormality", False),
        "stability_margin": ("stability_margin", True),
        "lyapunov_exponent": ("lyapunov_exponent", False),
        "settle_steps": ("settle_steps", False),
    }
    axes = tuple(name for name, _ in stability.values())
    maximize = tuple(flag for _, flag in stability.values())
    assert len(axes) == 6

    vectors = [
        dict(zip(axes, (0.90, 1.05, 1.17, 0.10, -0.10, 30.0), strict=True)),
        dict(zip(axes, (0.90, 1.05, 1.17, 0.10, -0.10, 12.0), strict=True)),
    ]
    assert _keep(vectors, axes[:2], maximize[:2]) == [0, 1], (
        "identical rho and sigma: two axes cannot separate these cells"
    )
    assert _keep(vectors, axes, maximize) == [1], (
        "settle_steps separates them, so the front is one cell wide"
    )
