"""Connection lifecycle and shared state for the evidence store."""

from __future__ import annotations

import logging
import threading
import time
from typing import TYPE_CHECKING, Any, ClassVar, Self

import duckdb

from computronium.experiment.evidence.artifacts import ArtifactStore
from computronium.experiment.evidence.mirror import is_lock_conflict, publish_mirror
from computronium.experiment.schema.versioning import current_schema_version

from ._models import StoreConfig, StoreError

if TYPE_CHECKING:
    from computronium.experiment.schema.record import Record
    from computronium.experiment.schema.run_spec import RunSpec

logger = logging.getLogger(__name__)

_SCHEMA_INIT_ATTEMPTS = 5
_SCHEMA_INIT_BACKOFF_S = 0.1
_CONNECT_ATTEMPTS = 5


class _StoreBase:
    """Connection lifecycle, mirror publication and writer state."""

    _SCHEMA_VERSION: ClassVar[int] = current_schema_version()
    SUPPORTED_SCHEMA_VERSIONS: ClassVar[frozenset[int]] = frozenset({_SCHEMA_VERSION})

    _config: StoreConfig
    _conn: duckdb.DuckDBPyConnection | None
    _write_lock: threading.RLock
    _initialized: bool
    _artifact_store: ArtifactStore | None
    _last_mirror: float

    def __init__(self, config: StoreConfig) -> None:
        self._config = config
        self._conn: duckdb.DuckDBPyConnection | None = None
        self._write_lock = threading.RLock()
        self._initialized = False
        self._artifact_store: ArtifactStore | None = None
        self._last_mirror: float = 0.0

    def __enter__(self) -> Self:
        self._conn = self._connect()
        if not self._initialized and not self._config.read_only:
            if not self._schema_present():
                try:
                    self._init_schema()
                except duckdb.Error:
                    # Another connection is creating the schema right now.
                    if not self._schema_present():
                        raise
            self._initialized = True
        # Initialize artifact store
        self._artifact_store = ArtifactStore(
            conn=self._conn,
            write_lock=self._write_lock,
            inline_threshold_mb=self._config.artifact_inline_threshold_mb,
            external_store_path=self._config.artifact_external_path,
        )
        self._assert_identity_recomputable()
        return self

    def _connect(self) -> duckdb.DuckDBPyConnection:
        """Open the connection, waiting out a reader that holds the file.

        DuckDB refuses a connection whose configuration differs from the one
        the file already has in this process: a read-only reader and a
        read-write writer cannot share the file, and the second one to ask is
        turned away. A reader that holds it for a moment — the dashboard
        polling the store while a campaign starts — must not stop the writer
        from running, so the writer waits for the reader to let go.

        The lock is exclusive across processes too. A reader does not wait
        that out: a writer in another process holds the file for the whole
        run, and the reader's answer is the mirror the writer publishes, not
        a wait that could last minutes.
        """
        delay = 0.2
        for attempt in range(_CONNECT_ATTEMPTS):
            try:
                return duckdb.connect(
                    str(self._config.path),
                    read_only=self._config.read_only,
                )
            except duckdb.Error as exc:
                waitable = not self._config.read_only and is_lock_conflict(exc)
                if not waitable or attempt == _CONNECT_ATTEMPTS - 1:
                    raise
                logger.debug(
                    "Store %s is held by another reader in another mode; waiting",
                    self._config.path,
                )
                time.sleep(delay)
                delay *= 2
        msg = "the store could not be opened"
        raise StoreError(msg)

    def _publish_mirror(self, *, force: bool = False) -> None:
        """Publish a copy of the store a reader in another process can open.

        DuckDB's lock is exclusive, so a dashboard in another terminal cannot
        open a store this process is writing: it sees nothing until the run
        ends. The mirror is the picture the writer publishes for that reader,
        and it is published at most once per ``mirror_interval``.
        """
        target = self._config.mirror_path
        if target is None or self._conn is None:
            return
        if str(self._config.path) == ":memory:":
            # A store that lives in memory has nothing to copy.
            return
        now = time.monotonic()
        if not force and now - self._last_mirror < self._config.mirror_interval:
            return
        try:
            publish_mirror(self._conn, target)
        except Exception as exc:  # ruff: ignore[blind-except] - a mirror is a convenience
            logger.debug("Mirror %s could not be published: %s", target, exc)
            return
        self._last_mirror = now

    def _assert_identity_recomputable(self) -> None:
        """Refuse a store that cannot reproduce a record's ``measurement_key``.

        ``param_budget`` and ``checkpoint_every_n`` are part of the key and were
        not persisted in older stores, so a store written before they were added
        reads every schedule back with defaults and no stored key recomputes from
        its own record. Appending to such a store fails deep in DuckDB instead,
        so it is refused here.
        """
        if self._conn is None:
            return
        row = self._conn.execute(
            "SELECT data_type FROM information_schema.columns "
            "WHERE table_name = 'records' AND column_name = 'schedule'"
        ).fetchone()
        if row is not None and (
            "param_budget" not in str(row[0]) or "checkpoint_every_n" not in str(row[0])
        ):
            msg = (
                f"store {self._config.path} has missing schedule fields; its "
                "measurement_key cannot be recomputed from a stored record. "
                "Write a new store."
            )
            raise StoreError(msg)

    def _validate_record_provenance(self, record: Record) -> None:
        """Validate that a record carries complete provenance metadata.

        Enforces the provenance contract: every record must have
        run_id, code_sha, config_sha256, seed_list, env_fingerprint,
        task_versions, hardware_hash.
        """
        prov = record.provenance
        required_fields = [
            ("code_sha", prov.code_sha),
            ("policy", prov.policy),
            ("dataset", prov.dataset),
            ("dataset_version", prov.dataset_version),
        ]
        for field_name, value in required_fields:
            if not value or value == "unknown":
                raise ValueError(
                    f"Record {record.measurement_key[:12]} missing required provenance field: {field_name}"
                )

        # Validate env fingerprint exists
        if not prov.env:
            raise ValueError(
                f"Record {record.measurement_key[:12]} missing env fingerprint"
            )

    def __exit__(
        self,
        exc_type: object,
        exc_val: BaseException | None,
        exc_tb: object,
    ) -> None:
        if self._conn is not None:
            if not self._config.read_only:
                self._publish_mirror(force=True)
                self._checkpoint()
            self._conn.close()
            self._conn = None
        self._artifact_store = None

    def _checkpoint(self) -> None:
        """Fold the write-ahead log into the database file, best effort.

        A checkpoint needs exclusive write access, so it fails while another
        connection holds a write transaction — a dashboard reading a store a
        campaign is writing, for instance. The log is durable without it, and
        a failed checkpoint must not keep the connection open.
        """
        if self._conn is None:
            return
        try:
            self._conn.execute("CHECKPOINT")
        except duckdb.Error as exc:
            logger.debug("Checkpoint deferred: %s", exc)

    @property
    def is_open(self) -> bool:
        """Whether the store is inside its connection context."""
        return self._conn is not None

    @property
    def artifacts(self) -> ArtifactStore:
        """Access the artifact store."""
        if self._artifact_store is None:
            raise StoreError("Artifact store not initialized (enter context first)")
        return self._artifact_store

    # Cross-mixin contract: each is implemented by one concern module.
    def _import_artifacts(self, artifacts_data: list[dict[str, Any]]) -> int:
        raise NotImplementedError

    def _import_vector_index(self, vectors_data: list[dict[str, Any]]) -> int:
        raise NotImplementedError

    def _init_schema(self) -> None:
        raise NotImplementedError

    @staticmethod
    def _read_spec(run_id: str, raw: str | None) -> RunSpec | None:
        raise NotImplementedError

    def _row_to_record(self, row: tuple) -> Record:
        raise NotImplementedError

    def _schema_present(self) -> bool:
        raise NotImplementedError

    def append(self, record: Record) -> Record:
        raise NotImplementedError
