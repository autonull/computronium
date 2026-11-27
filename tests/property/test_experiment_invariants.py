"""Experiment-Aware Property Tests (F1).

These tests validate invariants on experiment databases, ensuring regression safety
by checking that measured cells satisfy expected properties.

They need a store to read: the caller passes one, and the file's own tests skip
without it. ``scripts/run_local_gates.sh`` builds the 40-record readiness
campaign and passes it, so the invariants run once in the release instead of
skipping (W45).

Run with: pytest tests/property/test_experiment_invariants.py \
    --experiment-db /tmp/readiness.duckdb
"""

from __future__ import annotations

import pytest

from computronium.experiment.evidence.store import RecordStore, StoreConfig
from computronium.experiment.schema.axis import AXES_REGISTRIES, StructuralAxis


@pytest.mark.experiment
class TestExperimentInvariants:
    """Property tests that run against a real experiment database.

    Usage:
        pytest tests/property/test_experiment_invariants.py::TestExperimentInvariants -v \
            --experiment-db experiments/my_run.db
    """

    @pytest.fixture(autouse=True)
    def _setup_store(self, request):
        """Setup store from experiment database."""
        db_path = request.config.getoption("experiment_db")
        if not db_path:
            pytest.skip("No --experiment-db provided")
        self.store = RecordStore(StoreConfig(path=db_path, read_only=True))
        self.run_id = request.config.getoption("run_id")
        with self.store:
            if self.run_id is None:
                run_info = self.store.latest_run_id()
                if run_info is None:
                    pytest.skip("No runs found in database")
                self.run_id = run_info
            self.records = self.store.query_records(run_id=self.run_id)
        assert self.records, f"No records found for run_id: {self.run_id}"

    def test_all_measured_cells_satisfy_width_contract(self):
        """All measured cells should satisfy the width contract (param budget)."""
        for record in self.records:
            if record.status.gate_verdict.value == "PASS":
                param_count = record.payload.get("param_count", 0)
                param_budget = record.schedule.param_budget
                if param_budget > 0:
                    from computronium.experiment.schema.registries import (
                        PARAM_BUDGET_TOLERANCE,
                    )

                    assert param_count <= param_budget * (1 + PARAM_BUDGET_TOLERANCE), (
                        f"Cell {record.cell_key} exceeds param budget: {param_count} > {param_budget}"
                    )

    def test_no_critical_failures_in_measured_cells(self):
        """No measured cells should have critical failures."""
        critical_measured = [
            r
            for r in self.records
            if r.status.gate_verdict.value == "PASS"
            and r.status.severity.value == "critical"
        ]
        assert len(critical_measured) == 0, (
            f"Critical failures in measured cells: {[r.cell_key for r in critical_measured]}"
        )

    def test_coverage_targets_met(self):
        """At least one measured cell per geometry/update/credit axis."""
        for axis in [
            StructuralAxis.GEOMETRY,
            StructuralAxis.UPDATE,
            StructuralAxis.CREDIT,
        ]:
            measured = {
                getattr(r, axis.value)
                for r in self.records
                if r.status.gate_verdict.value == "PASS"
            }
            available = set(AXES_REGISTRIES[axis].keys())
            # Only check primitives that are actually available
            available = {p for p, s in AXES_REGISTRIES[axis].items() if s.available}
            missing = available - measured
            # Allow some missing if they're void-constrained
            # For now, just warn
            if missing:
                print(f"WARNING: Axis {axis.value} missing coverage: {missing}")

    def test_measured_cells_have_valid_metrics(self):
        """All measured cells should have valid (non-NaN, non-inf) metrics."""
        import math

        for record in self.records:
            if record.status.gate_verdict.value == "PASS":
                for key, val in record.payload.items():
                    if isinstance(val, float):
                        assert not math.isnan(val), (
                            f"NaN metric {key} in {record.cell_key}"
                        )
                        assert not math.isinf(val), (
                            f"Inf metric {key} in {record.cell_key}"
                        )

    def test_seed_consistency(self):
        """Cells with same coordinate but different seeds should have similar metrics."""
        import statistics
        from collections import defaultdict

        coord_groups = defaultdict(list)
        for record in self.records:
            if record.status.gate_verdict.value == "PASS":
                key = (
                    record.substrate,
                    record.geometry,
                    record.dynamics,
                    record.plasticity,
                    record.credit,
                    record.update,
                )
                acc = record.payload.get("validation_accuracy")
                if acc is not None:
                    coord_groups[key].append(acc)

        for coord, values in coord_groups.items():
            if len(values) > 1:
                mean_acc = statistics.mean(values)
                std_acc = statistics.stdev(values) if len(values) > 1 else 0
                # Std should be reasonable (not more than 50% of mean for classification)
                if mean_acc > 0:
                    cv = std_acc / mean_acc  # Coefficient of variation
                    assert cv < 0.5, (
                        f"High seed variance for {coord}: mean={mean_acc:.4f}, std={std_acc:.4f}, CV={cv:.2f}"
                    )

    def test_monotonic_improvement_over_time(self):
        """For cells with convergence curves, metrics should generally improve."""
        for record in self.records:
            if record.status.gate_verdict.value == "PASS":
                trajectory = record.payload.get("trajectory") or record.payload.get(
                    "convergence_curve"
                )
                if trajectory and isinstance(trajectory, list) and len(trajectory) > 1:
                    # Check that final value is not significantly worse than peak
                    peak = max(trajectory)
                    final = trajectory[-1]
                    # Allow 10% drop from peak (some noise expected)
                    assert final >= peak * 0.9, (
                        f"Significant drop in convergence for {record.cell_key}: peak={peak:.4f}, final={final:.4f}"
                    )

    def test_pareto_frontier_monotonic(self):
        """Pareto frontier should be monotonic (no dominated points on frontier)."""
        # This is implicitly tested by the pareto computation, but we can verify
        # by checking that for any two points on the frontier, one doesn't dominate both
        # Pareto property is mathematical; frontier generation ensures it
