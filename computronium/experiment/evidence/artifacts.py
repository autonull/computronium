"""Unified artifact storage in DuckDB.

Implements WP5 deliverable: evidence/artifacts.py — unified artifact storage
in DuckDB artifacts table. Single transaction with record append via
RecordStore.append_with_artifacts(). No CEEC dependency, no reconciliation.

Artifact size policy:
- small artifact (≤ 10 MB default, configurable) → DuckDB BLOB in artifacts.bytes
- large artifact → external content-addressed store (filesystem/S3/GCS)
  + transactional manifest reference in artifacts table
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import duckdb


class ArtifactRole(StrEnum):
    """Role of an artifact in the experiment."""

    CONFIG = "config"
    FIGURE = "figure"
    REPRODUCER = "reproducer"
    KERNEL = "kernel"
    MODEL_CHECKPOINT = "model_checkpoint"
    LOG = "log"
    DATA = "data"
    OTHER = "other"


class ArtifactStorage(StrEnum):
    """Storage backend for an artifact."""

    INLINE = "inline"  # Stored in DuckDB BLOB
    EXTERNAL = "external"  # Stored externally, manifest in DB


@dataclass(frozen=True, slots=True)
class ArtifactInput:
    """Input for storing an artifact."""

    bytes: bytes | None = None
    role: ArtifactRole = ArtifactRole.OTHER
    external_uri: str | None = None
    external_size: int | None = None
    external_checksum: str | None = None
    digest: str | None = None  # Pre-computed digest (optional)

    def __post_init__(self) -> None:
        if self.bytes is None and self.external_uri is None:
            raise ValueError("Either bytes or external_uri must be provided")
        if self.bytes is not None and self.external_uri is not None:
            raise ValueError("Provide either bytes or external_uri, not both")


@dataclass(frozen=True, slots=True)
class Artifact:
    """Stored artifact metadata."""

    digest: str
    role: ArtifactRole
    storage: ArtifactStorage
    size: int
    record_id: str
    created_at: str
    # Inline storage
    bytes: bytes | None = None
    # External storage
    external_uri: str | None = None
    external_checksum: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "digest": self.digest,
            "role": self.role.value,
            "storage": self.storage.value,
            "size": self.size,
            "record_id": self.record_id,
            "created_at": self.created_at,
            "external_uri": self.external_uri,
            "external_checksum": self.external_checksum,
        }

    @classmethod
    def from_row(cls, row: tuple) -> Artifact:
        """Create Artifact from database row.

        Database columns: digest, bytes, role, record_id, created_at,
        external_uri, external_size, external_checksum
        """
        digest, data_bytes, role, record_id, created_at, ext_uri, ext_size, ext_checksum = row
        storage = ArtifactStorage.INLINE if data_bytes is not None else ArtifactStorage.EXTERNAL
        size = len(data_bytes) if data_bytes is not None else (ext_size or 0)
        return cls(
            digest=digest,
            role=ArtifactRole(role),
            storage=storage,
            size=size,
            record_id=record_id,
            created_at=created_at,
            bytes=data_bytes,
            external_uri=ext_uri,
            external_checksum=ext_checksum,
        )


class ArtifactStore:
    """Artifact store backed by DuckDB artifacts table.

    Provides content-addressed storage with automatic inline/external
    routing based on size threshold.
    """

    def __init__(
        self,
        conn: duckdb.DuckDBPyConnection,
        write_lock: Any,  # threading.Lock
        inline_threshold_mb: float = 10.0,
        external_store_path: Path | None = None,
    ) -> None:
        self._conn = conn
        self._write_lock = write_lock
        self._inline_threshold = int(inline_threshold_mb * 1024 * 1024)
        self._external_store_path = external_store_path or Path.cwd() / "artifacts"

    def _ensure_external_dir(self) -> None:
        """Ensure external artifact directory exists."""
        self._external_store_path.mkdir(parents=True, exist_ok=True)

    def _compute_digest(self, data: bytes) -> str:
        """Compute SHA256 digest of bytes."""
        return hashlib.sha256(data).hexdigest()

    def _store_inline(
        self,
        digest: str,
        role: ArtifactRole,
        record_id: str,
        data: bytes,
    ) -> Artifact:
        """Store artifact inline in DuckDB."""
        self._conn.execute(
            """
            INSERT INTO artifacts (digest, bytes, role, record_id, created_at,
                                   external_uri, external_size, external_checksum)
            VALUES (?, ?, ?, ?, ?, NULL, NULL, NULL)
            ON CONFLICT (digest) DO NOTHING
            """,
            [digest, data, role.value, record_id, datetime.now()],
        )
        return Artifact(
            digest=digest,
            role=role,
            storage=ArtifactStorage.INLINE,
            size=len(data),
            record_id=record_id,
            created_at=datetime.now().isoformat(),
            bytes=data,
        )

    def _store_external(
        self,
        digest: str,
        role: ArtifactRole,
        record_id: str,
        external_uri: str,
        external_size: int,
        external_checksum: str,
    ) -> Artifact:
        """Register external artifact in DuckDB."""
        self._conn.execute(
            """
            INSERT INTO artifacts (digest, bytes, role, record_id, created_at,
                                   external_uri, external_size, external_checksum)
            VALUES (?, NULL, ?, ?, ?, ?, ?, ?)
            ON CONFLICT (digest) DO NOTHING
            """,
            [
                digest,
                role.value,
                record_id,
                datetime.now(),
                external_uri,
                external_size,
                external_checksum,
            ],
        )
        return Artifact(
            digest=digest,
            role=role,
            storage=ArtifactStorage.EXTERNAL,
            size=external_size,
            record_id=record_id,
            created_at=datetime.now().isoformat(),
            external_uri=external_uri,
            external_checksum=external_checksum,
        )

    def put(self, artifact_input: ArtifactInput, record_id: str) -> Artifact:
        """Store an artifact, automatically choosing inline or external.

        Args:
            artifact_input: The artifact to store
            record_id: The record this artifact belongs to

        Returns:
            The stored Artifact with metadata
        """
        if artifact_input.bytes is not None:
            # Inline or external based on size
            data = artifact_input.bytes
            digest = artifact_input.digest or self._compute_digest(data)

            if len(data) <= self._inline_threshold:
                with self._write_lock:
                    return self._store_inline(
                        digest, artifact_input.role, record_id, data
                    )
            else:
                # Too large for inline, store externally
                self._ensure_external_dir()
                ext_path = self._external_store_path / digest[:2] / digest
                ext_path.parent.mkdir(parents=True, exist_ok=True)
                ext_path.write_bytes(data)
                external_uri = f"file://{ext_path.absolute()}"
                external_checksum = digest  # Same as content digest

                with self._write_lock:
                    return self._store_external(
                        digest,
                        artifact_input.role,
                        record_id,
                        external_uri,
                        len(data),
                        external_checksum,
                    )

        else:
            # External artifact - register manifest only
            if not (
                artifact_input.external_uri
                and artifact_input.external_size is not None
                and artifact_input.external_checksum
            ):
                raise ValueError("External artifact requires external_uri, external_size, and external_checksum")

            digest = artifact_input.digest or artifact_input.external_checksum

            with self._write_lock:
                return self._store_external(
                    digest,
                    artifact_input.role,
                    record_id,
                    artifact_input.external_uri,
                    artifact_input.external_size,
                    artifact_input.external_checksum,
                )

    def get(self, digest: str) -> bytes | None:
        """Retrieve artifact bytes by digest.

        For inline artifacts, reads from DuckDB.
        For external artifacts, reads from external store.
        """
        row = self._conn.execute(
            "SELECT storage, bytes, external_uri FROM artifacts WHERE digest = ?",
            [digest],
        ).fetchone()

        if row is None:
            return None

        storage, data, external_uri = row

        if storage == ArtifactStorage.INLINE.value:
            return data
        else:
            if external_uri and external_uri.startswith("file://"):
                path = Path(external_uri[7:])  # Remove "file://"
                if path.exists():
                    return path.read_bytes()
            return None

    def get_metadata(self, digest: str) -> Artifact | None:
        """Get artifact metadata by digest."""
        row = self._conn.execute(
            "SELECT * FROM artifacts WHERE digest = ?", [digest]
        ).fetchone()
        if row is None:
            return None
        return Artifact.from_row(row)

    def get_for_record(self, record_id: str) -> list[Artifact]:
        """Get all artifacts for a record."""
        rows = self._conn.execute(
            """SELECT digest, bytes, role, record_id, created_at,
                      external_uri, external_size, external_checksum
               FROM artifacts WHERE record_id = ?""",
            [record_id],
        ).fetchall()
        return [Artifact.from_row(row) for row in rows]

    def delete(self, digest: str) -> bool:
        """Delete an artifact (only if not referenced by other records)."""
        # Check if referenced by other records
        result = self._conn.execute(
            "SELECT COUNT(*) FROM artifacts WHERE digest = ?", [digest]
        ).fetchone()
        ref_count = result[0] if result else 0

        if ref_count > 1:
            # Still referenced, don't delete
            return False

        # Get artifact to clean up external file if needed
        artifact = self.get_metadata(digest)
        if (
            artifact
            and artifact.storage == ArtifactStorage.EXTERNAL
            and artifact.external_uri
            and artifact.external_uri.startswith("file://")
        ):
            path = Path(artifact.external_uri[7:])
            if path.exists():
                path.unlink(missing_ok=True)

        with self._write_lock:
            self._conn.execute("DELETE FROM artifacts WHERE digest = ?", [digest])
        return True

    def list_by_role(self, role: ArtifactRole, limit: int = 100) -> list[Artifact]:
        """List artifacts by role."""
        rows = self._conn.execute(
            "SELECT * FROM artifacts WHERE role = ? LIMIT ?", [role.value, limit]
        ).fetchall()
        return [Artifact.from_row(row) for row in rows]

    def total_size(self, record_id: str | None = None) -> int:
        """Get total artifact size, optionally for a specific record."""
        if record_id:
            result = self._conn.execute(
                "SELECT SUM(size) FROM artifacts WHERE record_id = ?", [record_id]
            ).fetchone()
        else:
            result = self._conn.execute("SELECT SUM(size) FROM artifacts").fetchone()
        return result[0] if result and result[0] is not None else 0


# =============================================================================
# External Store Adapters (S3, GCS, etc.)
# =============================================================================


class ExternalStore:
    """Abstract base for external artifact stores."""

    def put(self, digest: str, data: bytes) -> tuple[str, str]:
        """Store data externally. Returns (uri, checksum)."""
        raise NotImplementedError

    def get(self, uri: str) -> bytes | None:
        """Retrieve data from external URI."""
        raise NotImplementedError

    def delete(self, uri: str) -> bool:
        """Delete external artifact."""
        raise NotImplementedError


class FilesystemExternalStore(ExternalStore):
    """External artifact store on local filesystem."""

    def __init__(self, base_path: Path) -> None:
        self.base_path = base_path
        self.base_path.mkdir(parents=True, exist_ok=True)

    def put(self, digest: str, data: bytes) -> tuple[str, str]:
        path = self.base_path / digest[:2] / digest
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return f"file://{path.absolute()}", digest

    def get(self, uri: str) -> bytes | None:
        if uri.startswith("file://"):
            path = Path(uri[7:])
            if path.exists():
                return path.read_bytes()
        return None

    def delete(self, uri: str) -> bool:
        if uri.startswith("file://"):
            path = Path(uri[7:])
            if path.exists():
                path.unlink()
                return True
        return False


# S3 and GCS adapters would go here when needed
# class S3ExternalStore(ExternalStore): ...
# class GCSExternalStore(ExternalStore): ...


__all__ = [
    "Artifact",
    "ArtifactInput",
    "ArtifactRole",
    "ArtifactStorage",
    "ArtifactStore",
    "ExternalStore",
    "FilesystemExternalStore",
]
