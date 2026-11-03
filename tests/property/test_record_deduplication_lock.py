"""Lock: record upsert deduplicates by (cell_key, seed, fidelity) composite key.

WS1.1 acceptance: SELECT COUNT(*) == SELECT COUNT(DISTINCT cell_key, seed, fidelity)
"""

from __future__ import annotations

import tempfile
from pathlib import Path

from computronium.experiment.evidence.store import RecordStore, StoreConfig
from computronium.experiment.schema import (
    Coordinate,
    DataOrigin,
    FailureCause,
    GateVerdict,
    Maturity,
    Provenance,
    Record,
    ReproducibilityClass,
    Schedule,
    Severity,
    Status,
)


def _make_record(
    seed: int = 0,
    fidelity: str = "L0",
    geometry: str = "feedforward",
    dynamics: str = "energy_minimization",
    run_id: str = "run1",
    **payload_overrides,
) -> Record:
    """Create a test record with given seed, fidelity, and coordinate axes."""
    coord = Coordinate(
        substrate="digital",
        geometry=geometry,
        dynamics=dynamics,
        plasticity="null",
        credit="thermodynamic_contrast",
        update="euclidean",
        params={},
    )
    sched = Schedule(
        fidelity=fidelity,
        seed=seed,
        n_seeds=1,
        epochs=1,
        batch_limit=10,
        budget_id="test",
        task_id="digits",
    )
    prov = Provenance(
        env={"hardware_class": "test_cpu", "cpu_count": "4"},
        dataset="digits",
        dataset_version="1.0",
        code_sha="test_sha",
        policy="test",
        links={"run_id": run_id},
        data_origin=DataOrigin.EXPLORATION,
    )
    status = Status(
        gate_verdict=GateVerdict.PASS_,
        defect="",
        cause=FailureCause.UNKNOWN,
        severity=Severity.LOW,
        quarantine=False,
        maturity=Maturity.L0,
        uncertainty={},
        reproducibility=ReproducibilityClass.REPLAYABLE,
        assessment_procedure_version="1.0",
        ceec_link=None,
    )
    payload = {"val_acc": 0.9, "walltime_s": 1.0, **payload_overrides}
    return Record.create(
        run_id=run_id,
        coordinate=coord,
        schedule=sched,
        provenance=prov,
        status=status,
        payload=payload,
    )


class TestRecordDeduplicationLock:
    """Tests enforcing record deduplication by composite key."""

    def test_upsert_same_cell_key_seed_fidelity_keeps_latest(self) -> None:
        """Same (cell_key, seed, fidelity) → exactly one record, latest wins."""
        with tempfile.TemporaryDirectory() as tmpdir:
            store_path = Path(tmpdir) / "test.duckdb"
            config = StoreConfig(path=store_path)

            with RecordStore(config) as store:
                run_id = store.create_run()

                # Create two records with same cell_key, seed, fidelity but different val_acc
                rec1 = _make_record(seed=0, fidelity="L0", run_id=run_id, val_acc=0.8)
                rec2 = _make_record(seed=0, fidelity="L0", run_id=run_id, val_acc=0.9)

                # Append both - second should upsert (replace) first
                store.append(rec1)
                store.append(rec2)

                # Query records
                records = store.query_records(run_id=run_id)

                # Should have exactly ONE record for this cell_key+seed+fidelity
                matching = [
                    r
                    for r in records
                    if r.cell_key == rec1.cell_key
                    and r.schedule.seed == 0
                    and r.schedule.fidelity == "L0"
                ]
                assert len(matching) == 1, f"Expected 1 record, got {len(matching)}"

                # The surviving record should be the latest (higher val_acc)
                assert matching[0].payload["val_acc"] == 0.9

    def test_different_seeds_different_records(self) -> None:
        """Different seeds for same cell_key → separate records."""
        with tempfile.TemporaryDirectory() as tmpdir:
            store_path = Path(tmpdir) / "test.duckdb"
            config = StoreConfig(path=store_path)

            with RecordStore(config) as store:
                run_id = store.create_run()

                rec1 = _make_record(seed=0, fidelity="L0", run_id=run_id)
                rec2 = _make_record(seed=1, fidelity="L0", run_id=run_id)

                store.append(rec1)
                store.append(rec2)

                records = store.query_records(run_id=run_id)
                matching = [
                    r
                    for r in records
                    if r.cell_key == rec1.cell_key and r.schedule.fidelity == "L0"
                ]
                assert len(matching) == 2, (
                    f"Expected 2 records (different seeds), got {len(matching)}"
                )

    def test_different_fidelity_different_records(self) -> None:
        """Different fidelity for same cell_key → separate records."""
        with tempfile.TemporaryDirectory() as tmpdir:
            store_path = Path(tmpdir) / "test.duckdb"
            config = StoreConfig(path=store_path)

            with RecordStore(config) as store:
                run_id = store.create_run()

                rec1 = _make_record(seed=0, fidelity="L0", run_id=run_id)
                rec2 = _make_record(seed=0, fidelity="L1", run_id=run_id)

                store.append(rec1)
                store.append(rec2)

                records = store.query_records(run_id=run_id)
                matching = [
                    r
                    for r in records
                    if r.cell_key == rec1.cell_key and r.schedule.seed == 0
                ]
                assert len(matching) == 2, (
                    f"Expected 2 records (different fidelity), got {len(matching)}"
                )

    def test_different_cell_keys_different_records(self) -> None:
        """Different coordinates (different cell_keys) → separate records."""
        with tempfile.TemporaryDirectory() as tmpdir:
            store_path = Path(tmpdir) / "test.duckdb"
            config = StoreConfig(path=store_path)

            with RecordStore(config) as store:
                run_id = store.create_run()

                # Create records with different coordinates (different cell_keys)
                rec1 = _make_record(
                    seed=0, fidelity="L0", geometry="feedforward", run_id=run_id
                )
                rec2 = _make_record(
                    seed=0, fidelity="L0", geometry="recurrent", run_id=run_id
                )

                store.append(rec1)
                store.append(rec2)

                records = store.query_records(run_id=run_id)
                assert len(records) == 2, (
                    f"Expected 2 records (different cell_keys), got {len(records)}"
                )

    def test_count_matches_distinct_composite_key(self) -> None:
        """Total records == distinct (cell_key, seed, fidelity) combinations."""
        with tempfile.TemporaryDirectory() as tmpdir:
            store_path = Path(tmpdir) / "test.duckdb"
            config = StoreConfig(path=store_path)

            with RecordStore(config) as store:
                run_id = store.create_run()

                # Create records with various combinations
                combos = [
                    ("feedforward", "energy_minimization", 0, "L0"),
                    (
                        "feedforward",
                        "energy_minimization",
                        0,
                        "L0",
                    ),  # Duplicate - should upsert
                    ("feedforward", "energy_minimization", 1, "L0"),  # Different seed
                    (
                        "feedforward",
                        "energy_minimization",
                        0,
                        "L1",
                    ),  # Different fidelity
                    (
                        "recurrent",
                        "energy_minimization",
                        0,
                        "L0",
                    ),  # Different cell_key (geometry)
                ]

                for geometry, dynamics, seed, fidelity in combos:
                    rec = _make_record(
                        seed=seed,
                        fidelity=fidelity,
                        geometry=geometry,
                        dynamics=dynamics,
                        run_id=run_id,
                    )
                    store.append(rec)

                records = store.query_records(run_id=run_id)

                # Count distinct composite keys
                distinct_keys = set()
                for r in records:
                    distinct_keys.add((
                        r.cell_key,
                        r.schedule.seed,
                        r.schedule.fidelity,
                    ))

                assert len(records) == len(distinct_keys), (
                    f"Record count ({len(records)}) != distinct composite keys ({len(distinct_keys)})"
                )
                # Should be 4 unique combos (one duplicate upserted)
                assert len(records) == 4
                assert len(distinct_keys) == 4

    def test_upsert_preserves_highest_maturity(self) -> None:
        """Upsert keeps record with highest maturity/epochs when maturity differs."""
        with tempfile.TemporaryDirectory() as tmpdir:
            store_path = Path(tmpdir) / "test.duckdb"
            config = StoreConfig(path=store_path)

            with RecordStore(config) as store:
                run_id = store.create_run()

                # Create L0 record with L0 maturity
                coord = Coordinate(
                    substrate="digital",
                    geometry="feedforward",
                    dynamics="energy_minimization",
                    plasticity="null",
                    credit="thermodynamic_contrast",
                    update="euclidean",
                    params={},
                )
                sched = Schedule(
                    fidelity="L0",
                    seed=0,
                    n_seeds=1,
                    epochs=1,
                    batch_limit=10,
                    budget_id="test",
                    task_id="digits",
                )
                prov = Provenance(
                    env={"hardware_class": "test_cpu", "cpu_count": "4"},
                    dataset="digits",
                    dataset_version="1.0",
                    code_sha="test_sha",
                    policy="test",
                    links={"run_id": run_id},
                    data_origin=DataOrigin.EXPLORATION,
                )
                status_l0 = Status(
                    gate_verdict=GateVerdict.PASS_,
                    defect="",
                    cause=FailureCause.UNKNOWN,
                    severity=Severity.LOW,
                    quarantine=False,
                    maturity=Maturity.L0,
                    uncertainty={},
                    reproducibility=ReproducibilityClass.REPLAYABLE,
                    assessment_procedure_version="1.0",
                    ceec_link=None,
                )
                rec_l0 = Record.create(
                    run_id=run_id,
                    coordinate=coord,
                    schedule=sched,
                    provenance=prov,
                    status=status_l0,
                    payload={"val_acc": 0.8, "walltime_s": 1.0},
                )

                # Create L1 record (same coordinate, higher maturity)
                status_l1 = Status(
                    gate_verdict=GateVerdict.PASS_,
                    defect="",
                    cause=FailureCause.UNKNOWN,
                    severity=Severity.LOW,
                    quarantine=False,
                    maturity=Maturity.L1,
                    uncertainty={},
                    reproducibility=ReproducibilityClass.REPLAYABLE,
                    assessment_procedure_version="1.0",
                    ceec_link=None,
                )
                rec_l1 = Record.create(
                    run_id=run_id,
                    coordinate=coord,
                    schedule=sched,
                    provenance=prov,
                    status=status_l1,
                    payload={"val_acc": 0.9, "walltime_s": 1.0},
                )

                store.append(rec_l0)
                store.append(rec_l1)

                records = store.query_records(run_id=run_id)
                matching = [
                    r
                    for r in records
                    if r.cell_key == rec_l0.cell_key
                    and r.schedule.seed == 0
                    and r.schedule.fidelity == "L0"
                ]
                assert len(matching) == 1
                # Should keep the L1 maturity record (higher maturity)
                assert matching[0].status.maturity == Maturity.L1
