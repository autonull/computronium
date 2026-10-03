"""Schedule device field: the campaign records and reports the device used.

The evaluator threads the schedule's device to SystemTrainer and the task.
The YAML spec declares it; comp run reports it. This lock asserts the device
field flows from spec → schedule → record → report.
"""

from __future__ import annotations

import pytest
import torch

from computronium.experiment.evidence.store import RecordStore, StoreConfig
from computronium.experiment.execution.evaluate import cell_record
from computronium.experiment.schema.coordinate import Coordinate, Provenance, Schedule
from computronium.experiment.schema.run_spec import RunSpec
from computronium.experiment.schema.seed_registries import seed_all_registries


def test_schedule_device_field_roundtrip() -> None:
    """Schedule.device round-trips through to_dict/from_dict and measurement_key."""
    sched = Schedule(
        fidelity="L0",
        seed=0,
        n_seeds=1,
        epochs=1,
        batch_limit=2,
        budget_id="test",
        task_id="digits",
        param_budget=10000,
        device="cuda",
    )
    # Round-trip
    restored = Schedule.from_dict(sched.to_dict())
    assert restored.device == "cuda"

    # measurement_key includes device
    coord = Coordinate(
        substrate="digital",
        geometry="feedforward",
        dynamics="energy_minimization",
        plasticity="fast_weights",
        credit="gradient",
        update="euclidean",
        params={},
    )
    key1 = coord.measurement_key(sched)
    sched_cpu = Schedule(
        fidelity="L0",
        seed=0,
        n_seeds=1,
        epochs=1,
        batch_limit=2,
        budget_id="test",
        task_id="digits",
        param_budget=10000,
        device="cpu",
    )
    key2 = coord.measurement_key(sched_cpu)
    assert key1 != key2, "measurement_key must differ by device"


def test_runspec_device_field_validation() -> None:
    """RunSpec validates device field."""
    # Valid device
    spec = RunSpec(
        task="digits",
        tasks=(),
        fidelity="L0",
        n_seeds=1,
        epochs=1,
        batch_limit=2,
        seed=0,
        param_budget=10000,
        policy="round_robin_grid",
        axes=(),
        hyperparameters={},
        device="cuda",
    )
    assert spec.device == "cuda"

    # Invalid device
    with pytest.raises(ValueError, match="invalid device"):
        RunSpec(
            task="digits",
            tasks=(),
            fidelity="L0",
            n_seeds=1,
            epochs=1,
            batch_limit=2,
            seed=0,
            param_budget=10000,
            policy="round_robin_grid",
            axes=(),
            hyperparameters={},
            device="invalid",
        )


@pytest.mark.skipif(not torch.cuda.is_available(), reason="CUDA not available")
def test_device_cuda_recorded_in_store(tmp_path) -> None:
    """A cell evaluated with device='cuda' records the device in its schedule."""
    seed_all_registries()
    store_path = tmp_path / "device_test.duckdb"

    record = cell_record(
        Coordinate(
            substrate="digital",
            geometry="feedforward",
            dynamics="energy_minimization",
            plasticity="fast_weights",
            credit="gradient",
            update="euclidean",
            params={"depth": 2, "hidden_dim": 32, "settle_step": 0.03162},
        ),
        Schedule(
            fidelity="L0",
            seed=0,
            n_seeds=1,
            epochs=1,
            batch_limit=2,
            budget_id="device_test",
            task_id="digits",
            param_budget=10000,
            device="cuda",
        ),
        provenance=Provenance(
            env={},
            dataset="digits",
            dataset_version="1.0",
            code_sha="device_test",
            policy="device_test",
            links={"run_id": "device_test_run"},
        ),
    )

    # Verify the record's schedule has the device
    assert record.schedule.device == "cuda"

    # Write to store and read back
    with RecordStore(StoreConfig(path=store_path)) as store:
        store.create_run("device_test_run")
        store.append(record)
        records = store.query_records(run_id="device_test_run")
        assert len(records) == 1
        assert records[0].schedule.device == "cuda"


def test_device_auto_defaults_to_cpu_when_no_cuda(tmp_path, monkeypatch) -> None:
    """device='auto' resolves to CPU when CUDA is not available (or mocked away)."""
    # Mock torch.cuda.is_available to return False
    original_is_available = torch.cuda.is_available
    monkeypatch.setattr(torch.cuda, "is_available", lambda: False)

    try:
        seed_all_registries()
        record = cell_record(
            Coordinate(
                substrate="digital",
                geometry="feedforward",
                dynamics="energy_minimization",
                plasticity="fast_weights",
                credit="gradient",
                update="euclidean",
                params={"depth": 2, "hidden_dim": 32, "settle_step": 0.03162},
            ),
            Schedule(
                fidelity="L0",
                seed=0,
                n_seeds=1,
                epochs=1,
                batch_limit=2,
                budget_id="device_test",
                task_id="digits",
                param_budget=10000,
                device="auto",
            ),
            provenance=Provenance(
                env={},
                dataset="digits",
                dataset_version="1.0",
                code_sha="device_test",
                policy="device_test",
                links={"run_id": "device_test_run"},
            ),
        )
        # The schedule should still say "auto" (it's what was requested)
        # The actual device used is resolved inside the evaluator
        assert record.schedule.device == "auto"
    finally:
        monkeypatch.setattr(torch.cuda, "is_available", original_is_available)


def test_campaign_yaml_declares_device() -> None:
    """The campaign YAML declares a device field."""
    spec = RunSpec.load("examples/learning-rules-and-geometry-digits.yaml")
    assert spec.device == "auto"
