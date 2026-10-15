"""Fast unit test for Pareto frontier diverse selection (select_diverse).

Verifies the crowding-distance-based top-k selection used by exploit-axis
strategy. Uses synthetic ParetoPoints - no store, no training, runs in <1s.
"""

from __future__ import annotations

from computronium.experiment.optimization.multi_objective import (
    NormalizedObjective,
    ParetoFrontier,
    ParetoPoint,
)


def _make_point(
    cell_key: str,
    crowding: float,
    rank: int = 0,
    obj_vals: tuple[float, ...] = (0.5, 0.5),
) -> ParetoPoint:
    """Create a ParetoPoint with given crowding distance and objectives."""
    objs = tuple(
        NormalizedObjective(
            name=f"obj{i}",
            raw_value=v,
            normalized_value=v,
            direction="minimize",
            weight=1.0,
            normalizer=None,
            axis_tag=None,
            is_measured=True,
        )
        for i, v in enumerate(obj_vals)
    )
    return ParetoPoint(
        cell_key=cell_key,
        replication_key=f"{cell_key}_rep",
        objectives=objs,
        crowding_distance=crowding,
        rank=rank,
    )


def test_select_diverse_returns_frontier_when_k_ge_n() -> None:
    """If k >= number of front points, return all."""
    points = [
        _make_point("a", 1.0),
        _make_point("b", 2.0),
        _make_point("c", 0.5),
    ]
    frontier = ParetoFrontier(
        points=tuple(points),
        objective_names=("obj0", "obj1"),
        reference_point=None,
    )
    selected = frontier.select_diverse(5)
    assert len(selected) == 3
    assert {p.cell_key for p in selected} == {"a", "b", "c"}


def test_select_diverse_picks_highest_crowding() -> None:
    """With k < n, picks points with highest crowding distance."""
    points = [
        _make_point("low", 0.5),
        _make_point("mid", 2.0),
        _make_point("high", 5.0),
        _make_point("boundary1", float("inf")),
        _make_point("boundary2", float("inf")),
    ]
    frontier = ParetoFrontier(
        points=tuple(points),
        objective_names=("obj0", "obj1"),
        reference_point=None,
    )
    selected = frontier.select_diverse(3)
    assert len(selected) == 3
    keys = {p.cell_key for p in selected}
    # Should include both boundary points (inf) and one more
    assert "boundary1" in keys
    assert "boundary2" in keys
    assert "high" in keys
    assert "mid" not in keys
    assert "low" not in keys


def test_select_diverse_empty_frontier_returns_empty() -> None:
    """Empty frontier returns empty list."""
    frontier = ParetoFrontier(
        points=(),
        objective_names=("obj0", "obj1"),
        reference_point=None,
    )
    selected = frontier.select_diverse(5)
    assert selected == []


def test_select_diverse_preserves_order_by_crowding_desc() -> None:
    """Selected points are ordered by crowding distance descending."""
    points = [
        _make_point("a", 1.0),
        _make_point("b", 3.0),
        _make_point("c", 2.0),
        _make_point("d", float("inf")),
    ]
    frontier = ParetoFrontier(
        points=tuple(points),
        objective_names=("obj0", "obj1"),
        reference_point=None,
    )
    selected = frontier.select_diverse(3)
    assert [p.cell_key for p in selected] == ["d", "b", "c"]


def test_select_diverse_only_considers_rank_0() -> None:
    """Only rank-0 (front) points are considered, even if higher rank has higher crowding."""
    points = [
        _make_point("front_low", 1.0, rank=0),
        _make_point("front_high", 2.0, rank=0),
        _make_point("dominated_high_crowding", 100.0, rank=1),  # Should be ignored
    ]
    frontier = ParetoFrontier(
        points=tuple(points),
        objective_names=("obj0", "obj1"),
        reference_point=None,
    )
    selected = frontier.select_diverse(2)
    keys = {p.cell_key for p in selected}
    assert keys == {"front_low", "front_high"}
    assert "dominated_high_crowding" not in keys


def test_select_diverse_k_zero_returns_empty() -> None:
    """k=0 returns empty list."""
    points = [_make_point("a", 1.0)]
    frontier = ParetoFrontier(
        points=tuple(points),
        objective_names=("obj0", "obj1"),
        reference_point=None,
    )
    selected = frontier.select_diverse(0)
    assert selected == []


if __name__ == "__main__":
    import pytest

    pytest.main([__file__, "-v"])
