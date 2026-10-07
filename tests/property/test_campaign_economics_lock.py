"""D2 — Campaign Economics: the record price, published.

``comp status --run-id`` prints measured cost per record and a projected
completion (records done / records declared × s/record); the report prints
the same. A run that will take 4 hours must say so at 60 s, not at 3 hours.

Gate: a lock running a 10-cell narrowed store spec asserts the status output
contains a rate and a projection; falsifiable by removing the projection.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from pathlib import Path

from computronium.experiment.evidence.store import RecordStore, StoreConfig
from computronium.experiment.schema import (
    Domain,
    Scale,
    StructuralAxis,
    MEASURED_PARAM_BUDGET,
    AxisSelection,
    RunSpec,
    seed_all_registries,
)
from computronium.experiment.surface import cli
from computronium.experiment.surface.report import generate_run_report


def _build_narrowed_spec_path(tmp_path: Path) -> Path:
    """A 10-cell spec: 2 dynamics × 2 credits × 1 geometry × 1 task × ~2 sweep points × 1 seed."""
    spec = RunSpec(
        version=2,
        profile="d2_economics",
        task="digits",
        objectives=("validation_accuracy", "walltime_total"),
        stages=(
            "s1_frame",
            "s2_space",
            "s3_schedule",
            "s4_gate",
            "s5_compose",
            "s6_train",
            "s7_measure",
            "s8_record",
            "s9_attribute",
            "s10_decide",
            "s11_report",
        ),
        fidelity="L0",
        n_seeds=1,
        epochs=1,
        batch_limit=2,
        seed=0,
        budget_seconds=60.0,
        param_budget=MEASURED_PARAM_BUDGET,
        policy="round_robin_grid",
        device="cpu",
        axes=(
            AxisSelection(axis=StructuralAxis.SUBSTRATE, primitives=("digital",)),
            AxisSelection(axis=StructuralAxis.PLASTICITY, primitives=("null",)),
            AxisSelection(axis=StructuralAxis.UPDATE, primitives=("euclidean",)),
            AxisSelection(
                axis=StructuralAxis.DYNAMICS,
                primitives=("energy_minimization", "instantaneous"),
            ),
            AxisSelection(
                axis=StructuralAxis.CREDIT,
                primitives=("gradient", "thermodynamic_contrast"),
            ),
            AxisSelection(axis=StructuralAxis.GEOMETRY, primitives=("feedforward",)),
        ),
        hyperparameters={
            "hidden_dim": Domain(lo=32, hi=64, scale=Scale.LOG),
            "settle_step": Domain(lo=0.01, hi=0.1, scale=Scale.LOG),
            "update_lr": Domain(lo=0.01, hi=0.1, scale=Scale.LOG),
        },
    )
    spec_path = tmp_path / "d2_spec.yaml"
    import yaml

    spec_path.write_text(yaml.dump(spec.to_dict()))
    return spec_path


@pytest.fixture(scope="module")
def d2_store(tmp_path_factory):
    """Create a store with ~10 records for the economics test."""
    seed_all_registries()
    store_path = tmp_path_factory.mktemp("d2_economics") / "d2.duckdb"
    tmp_path = tmp_path_factory.mktemp("d2_spec")
    spec_path = _build_narrowed_spec_path(tmp_path)

    # Run the spec through the CLI
    exit_code = cli.main(["run", "--spec", str(spec_path), "--store", str(store_path)])
    # The run may exit early due to budget; we just need some records
    assert exit_code in {0, 130}, f"Run failed with exit code {exit_code}"

    with RecordStore(StoreConfig(path=store_path, read_only=True)) as store:
        run = store.query_runs()[0]
        yield store, run.run_id


def test_status_detailed_shows_cost_per_record_and_projection(d2_store):
    """Gate: ``comp status --detailed`` prints cost/record and projected completion."""
    store, run_id = d2_store

    # Capture the detailed status output
    import io
    import sys

    old_stdout = sys.stdout
    sys.stdout = io.StringIO()
    try:
        exit_code = cli.main([
            "status",
            "--store",
            str(store._config.path),
            "--run-id",
            run_id,
            "--detailed",
        ])
        output = sys.stdout.getvalue()
    finally:
        sys.stdout = old_stdout

    assert exit_code == 0, f"status command failed with {exit_code}"

    # Assert the output contains cost per record
    assert "Cost per Record:" in output, (
        f"Missing 'Cost per Record:' in output:\n{output}"
    )

    # Assert the output contains projected completion
    assert "Projected Total:" in output or "Remaining:" in output, (
        f"Missing projection in output:\n{output}"
    )

    # Assert the output contains progress
    assert "Progress:" in output, f"Missing 'Progress:' in output:\n{output}"

    print("\nD2 Status Output:")
    print(output)


def test_report_includes_economics_section(d2_store):
    """Gate: the generated report includes the Campaign Economics section."""
    store, run_id = d2_store

    report_text = generate_run_report(store, run_id)

    assert "Campaign Economics:" in report_text, (
        f"Missing 'Campaign Economics:' section in report:\n{report_text}"
    )

    # Should have cost per record if there are records
    from computronium.experiment.surface.report import ReportGenerator

    report = ReportGenerator(store)
    summary = report.run_summary(run_id)
    if summary and summary.record_count > 0 and summary.budget_consumed_s:
        assert "Cost per Record:" in report_text

    print("\nD2 Report Economics Section:")
    for line in report_text.splitlines():
        if (
            "Campaign Economics" in line
            or "Cost per Record" in line
            or "Projected" in line
            or "Progress" in line
        ):
            print(f"  {line}")


def test_status_json_includes_declared_cells(d2_store):
    """The JSON status output includes declared_cells field."""
    store, run_id = d2_store

    import io
    import sys

    old_stdout = sys.stdout
    sys.stdout = io.StringIO()
    try:
        exit_code = cli.main([
            "status",
            "--store",
            str(store._config.path),
            "--run-id",
            run_id,
        ])
        output = sys.stdout.getvalue()
    finally:
        sys.stdout = old_stdout

    assert exit_code == 0

    data = json.loads(output)
    assert "declared_cells" in data, f"Missing 'declared_cells' in JSON: {data}"
    assert data["declared_cells"] > 0, (
        f"declared_cells should be > 0: {data['declared_cells']}"
    )


def test_falsifiable_by_removing_projection():
    """Falsifiable: if we remove the projection logic, the gate fails.

    This test documents the expected behavior - if the projection code is
    removed, the assertions above will fail.
    """
    # This is a documentation test; the real falsification is manual:
    # comment out the projection in _print_detailed_status and watch this fail.


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
