"""Legacy-store migration and bootstrap helpers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from computronium.experiment.evidence.artifacts import ArtifactInput
from computronium.experiment.schema.coordinate import Provenance
from computronium.experiment.schema.record import Record

from ._models import DuplicateMeasurementError, RunInfo, StoreConfig
from ._store import RecordStore

if TYPE_CHECKING:
    from pathlib import Path


@dataclass(frozen=True, slots=True)
class MigrationReport:
    """Report of a store migration operation."""

    source_path: str
    target_path: str
    records_migrated: int
    runs_migrated: int
    artifacts_migrated: int
    schema_version_from: int
    schema_version_to: int
    warnings: tuple[str, ...]


def _migrate_runs(
    source_store: RecordStore, target_store: RecordStore
) -> tuple[list[RunInfo], int]:
    """Migrate runs from source to target store. Returns (source_runs, count)."""
    source_runs = source_store.query_runs()
    count = 0
    for run_info in source_runs:
        target_store.create_run(run_id=run_info.run_id, spec=run_info.spec)
        count += 1
    return source_runs, count


def _migrate_records(
    source_store: RecordStore,
    target_store: RecordStore,
    source_runs: list[RunInfo],
    default_code_sha: str,
    default_dataset: str,
    default_dataset_version: str,
) -> tuple[int, list[str]]:
    """Migrate records from source to target store. Returns (count, warnings)."""
    warnings: list[str] = []
    records_migrated = 0

    for run_info in source_runs:
        records = source_store.query_records(run_id=run_info.run_id)
        for record in records:
            enriched_prov = _enrich_provenance(
                record.provenance,
                default_code_sha=default_code_sha,
                default_dataset=default_dataset,
                default_dataset_version=default_dataset_version,
            )
            if enriched_prov is not record.provenance:
                warnings.append(
                    f"Enriched provenance for record {record.record_id[:12]}"
                )

            new_record = Record(
                record_id=record.record_id,
                seq=record.seq,
                run_id=record.run_id,
                schema_version=RecordStore._SCHEMA_VERSION,
                cell_key=record.cell_key,
                measurement_key=record.measurement_key,
                substrate=record.substrate,
                geometry=record.geometry,
                dynamics=record.dynamics,
                plasticity=record.plasticity,
                credit=record.credit,
                update=record.update,
                params=record.params,
                effective_params=record.effective_params,
                schedule=record.schedule,
                provenance=enriched_prov,
                status=record.status,
                payload=record.payload,
                unknown=record.unknown,
            )

            try:
                target_store.append(new_record)
                records_migrated += 1
            except DuplicateMeasurementError:
                warnings.append(
                    f"Skipped duplicate measurement_key: {record.measurement_key[:12]}"
                )

            # Migrate artifacts
            _migrate_record_artifacts(source_store, target_store, record, warnings)

    return records_migrated, warnings


def _migrate_record_artifacts(
    source_store: RecordStore,
    target_store: RecordStore,
    record: Record,
    warnings: list[str],
) -> None:
    """Migrate artifacts for a single record."""
    if target_store._config.read_only or target_store._artifact_store is None:
        return
    try:
        artifacts = source_store.artifacts.get_for_record(record.record_id)
        for artifact in artifacts:
            art_input = ArtifactInput(
                bytes=artifact.bytes,
                role=artifact.role,
                external_uri=artifact.external_uri,
                external_size=artifact.size
                if artifact.storage.value == "external"
                else None,
                external_checksum=artifact.external_checksum,
                digest=artifact.digest,
            )
            target_store.artifacts.put(art_input, record.record_id)
    except Exception as e:
        warnings.append(f"Failed to migrate artifacts for {record.record_id[:12]}: {e}")


def _migrate_checkpoints(
    source_store: RecordStore, target_store: RecordStore, source_runs: list[RunInfo]
) -> None:
    """Migrate checkpoints from source to target store."""
    for run_info in source_runs:
        checkpoint = source_store.load_checkpoint(run_info.run_id)
        if checkpoint:
            target_store.save_checkpoint(run_info.run_id, checkpoint)


def migrate_legacy_store(
    source_path: Path,
    target_path: Path,
    *,
    default_code_sha: str = "unknown",
    default_dataset: str = "unknown",
    default_dataset_version: str = "1.0",
) -> MigrationReport:
    """Migrate a legacy DuckDB store to the current schema.

    Reads records from the source store (any supported schema version),
    enriches them with required provenance fields, and writes to a new
    target store with the current schema.

    Args:
        source_path: Path to the legacy store file
        target_path: Path for the new migrated store
        default_code_sha: Fallback git SHA for records missing it
        default_dataset: Fallback dataset name
        default_dataset_version: Fallback dataset version

    Returns:
        MigrationReport with migration statistics
    """
    # Open source read-only
    source_store = RecordStore(StoreConfig(path=source_path, read_only=True))
    source_store.__enter__()

    # Create target store
    target_store = RecordStore(StoreConfig(path=target_path, read_only=False))
    target_store.__enter__()

    warnings: list[str] = []
    runs_migrated = 0
    artifacts_migrated = 0

    try:
        # Migrate runs first
        source_runs, runs_migrated = _migrate_runs(source_store, target_store)

        # Migrate records
        records_migrated, record_warnings = _migrate_records(
            source_store,
            target_store,
            source_runs,
            default_code_sha,
            default_dataset,
            default_dataset_version,
        )
        warnings.extend(record_warnings)

        # Migrate checkpoints
        _migrate_checkpoints(source_store, target_store, source_runs)

        # Collect all records for schema version calculation
        all_records: list[Record] = []
        for run_info in source_runs:
            all_records.extend(source_store.query_records(run_id=run_info.run_id))

        return MigrationReport(
            source_path=str(source_path),
            target_path=str(target_path),
            records_migrated=records_migrated,
            runs_migrated=runs_migrated,
            artifacts_migrated=artifacts_migrated,
            schema_version_from=min(r.schema_version for r in all_records)
            if all_records
            else 1,
            schema_version_to=RecordStore._SCHEMA_VERSION,
            warnings=tuple(warnings),
        )

    finally:
        source_store.__exit__(None, None, None)
        target_store.__exit__(None, None, None)


def _enrich_provenance(
    provenance: Provenance,
    *,
    default_code_sha: str,
    default_dataset: str,
    default_dataset_version: str,
) -> Provenance:
    """Enrich a provenance object with required fields if missing."""
    env = dict(provenance.env)
    if not env:
        env = {"migrated": "true"}

    code_sha = (
        provenance.code_sha if provenance.code_sha != "unknown" else default_code_sha
    )
    dataset = provenance.dataset if provenance.dataset != "unknown" else default_dataset
    dataset_version = (
        provenance.dataset_version
        if provenance.dataset_version != "1.0"
        else default_dataset_version
    )

    return Provenance(
        env=env,
        dataset=dataset,
        dataset_version=dataset_version,
        code_sha=code_sha,
        policy=provenance.policy or "migrated",
        links=dict(provenance.links),
        data_origin=provenance.data_origin,
        training_tasks=provenance.training_tasks,
        transfer_source_ids=provenance.transfer_source_ids,
        transfer_cutoff=provenance.transfer_cutoff,
        target_task=provenance.target_task,
        transfer_mode=provenance.transfer_mode,
    )


def bootstrap_stores(
    store_paths: list[Path],
    target_dir: Path,
    *,
    default_code_sha: str = "unknown",
    default_dataset: str = "unknown",
    default_dataset_version: str = "1.0",
) -> list[MigrationReport]:
    """Bootstrap multiple legacy stores into the current schema.

    Creates a new migrated store for each source store in target_dir.
    """
    target_dir.mkdir(parents=True, exist_ok=True)
    reports = []

    for source_path in store_paths:
        if not source_path.exists():
            continue
        target_path = target_dir / f"migrated_{source_path.name}"
        report = migrate_legacy_store(
            source_path,
            target_path,
            default_code_sha=default_code_sha,
            default_dataset=default_dataset,
            default_dataset_version=default_dataset_version,
        )
        reports.append(report)

    return reports


__all__ = ["MigrationReport", "bootstrap_stores", "migrate_legacy_store"]
