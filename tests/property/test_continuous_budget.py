"""ContinuousBudget semantics (TODO29 Phase 3) with an injected fake clock."""

from __future__ import annotations

from dataclasses import replace

import pytest

from computronium.autoscientist.broad_map import ContinuousBudget


class TestParse:
    def test_duration_units(self) -> None:
        for spec, seconds in (
            ("5m", 300.0),
            ("90s", 90.0),
            ("1h", 3600.0),
            ("45", 45.0),
        ):
            budget = ContinuousBudget.parse(spec, started_at=100.0)
            assert budget.soft_seconds == seconds
            assert budget.hard_seconds == seconds
            assert budget.started_at == 100.0

    @pytest.mark.parametrize("spec", ["", "5x", "m", "-5s", "1.2.3s", "five"])
    def test_parse_errors(self, spec: str) -> None:
        with pytest.raises(ValueError, match="invalid budget"):
            ContinuousBudget.parse(spec)

    def test_parse_defaults_to_monotonic_anchor(self) -> None:
        budget = ContinuousBudget.parse("1s")
        assert budget.started_at > 0


class TestExpiry:
    def test_soft_then_hard_ordering(self) -> None:
        budget = ContinuousBudget(started_at=0.0, soft_seconds=10.0, hard_seconds=20.0)
        assert not budget.soft_expired(9.999)
        assert budget.soft_expired(10.0)
        assert not budget.hard_expired(10.0)
        assert budget.hard_expired(20.0)

    def test_unbounded_budget_never_expires(self) -> None:
        budget = ContinuousBudget(started_at=0.0)
        assert not budget.soft_expired(1e12)
        assert not budget.hard_expired(1e12)

    def test_soft_cannot_expire_after_hard_at_same_value(self) -> None:
        budget = ContinuousBudget.parse("30s", started_at=0.0)
        assert budget.soft_expired(30.0) and budget.hard_expired(30.0)


class TestTarget:
    def test_target_reached_is_hard_cap(self) -> None:
        budget = ContinuousBudget(started_at=0.0, target_cells=3)
        assert not budget.target_reached()
        assert not budget.advance_by(2).target_reached()
        assert budget.advance_by(3).target_reached()

    def test_no_target_never_reached(self) -> None:
        assert not ContinuousBudget(started_at=0.0, done=10**9).target_reached()


class TestAdvance:
    def test_advance_is_immutable(self) -> None:
        budget = ContinuousBudget(started_at=0.0, soft_seconds=5.0, done=1)
        advanced = budget.advance()
        assert advanced is not budget
        assert advanced.done == 2
        assert budget.done == 1  # original untouched

    def test_advance_by(self) -> None:
        budget = ContinuousBudget(started_at=0.0).advance_by(7)
        assert budget.done == 7

    def test_advance_preserves_other_fields(self) -> None:
        budget = ContinuousBudget(
            started_at=3.0, soft_seconds=5.0, hard_seconds=9.0, target_cells=4, done=0
        )
        advanced = budget.advance()
        assert (
            advanced.started_at,
            advanced.soft_seconds,
            advanced.hard_seconds,
            advanced.target_cells,
        ) == (
            3.0,
            5.0,
            9.0,
            4,
        )


def test_precedence_target_beats_budget() -> None:
    """--target-cells is a hard cap; --budget a soft time cap: the first
    limit reached stops the burst (integration-level proof in
    tests/integration/test_continuous_burst.py)."""
    budget = ContinuousBudget.parse("1h", started_at=0.0).advance_by(3)
    assert not budget.target_reached()  # no target set: budget governs
    assert replace(budget, target_cells=3).target_reached()
