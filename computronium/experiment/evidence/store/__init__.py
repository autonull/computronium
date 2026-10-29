"""DuckDB-backed record store for experiment evidence.

The public surface is unchanged from the former single-module
``computronium.experiment.evidence.store``: schema creation, transactions,
artifact writes and queries live in separate concern modules, and
:class:`RecordStore` composes them.
"""

from __future__ import annotations

from computronium.experiment.evidence.store._migrations import (
    MigrationReport,
    bootstrap_stores,
    migrate_legacy_store,
)
from computronium.experiment.evidence.store._models import (
    DuplicateMeasurementError,
    ProvenanceModel,
    RecordInputModel,
    RecordOutputModel,
    RunInfo,
    ScheduleModel,
    StatusModel,
    StoreConfig,
    StoreError,
    TableName,
    TableSlice,
    UnsupportedSchemaVersionError,
    format_replication_key,
    validate_record_input,
    validate_record_output,
)
from computronium.experiment.evidence.store._store import RecordStore

__all__ = [
    "DuplicateMeasurementError",
    "MigrationReport",
    "ProvenanceModel",
    "RecordInputModel",
    "RecordOutputModel",
    "RecordStore",
    "RunInfo",
    "ScheduleModel",
    "StatusModel",
    "StoreConfig",
    "StoreError",
    "TableName",
    "TableSlice",
    "UnsupportedSchemaVersionError",
    "bootstrap_stores",
    "format_replication_key",
    "migrate_legacy_store",
    "validate_record_input",
    "validate_record_output",
]
