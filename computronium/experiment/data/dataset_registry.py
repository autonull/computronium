"""Dataset Registry: Versioned datasets with hash-verified splits (Phase E6).

Provides dataset versioning, integrity verification, and split management.
"""

from __future__ import annotations

import hashlib
import json
import logging
import subprocess  # ruff: ignore[suspicious-subprocess-import] -- used for controlled CLI subprocess calls (git)
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import duckdb

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class DatasetSplit:
    """A single dataset split (train/val/test)."""

    name: str
    path: str
    hash: str
    size_bytes: int
    num_samples: int
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class DatasetVersion:
    """A versioned dataset with splits."""

    dataset_id: str
    version: str  # Semantic version (e.g., "1.0.0")
    digest: str  # SHA256 of the entire dataset directory
    created_at: str
    description: str = ""
    splits: dict[str, DatasetSplit] = field(default_factory=dict)
    tags: dict[str, str] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    source_url: str | None = None
    source_hash: str | None = None


@dataclass
class DatasetRegistration:
    """Input for registering a dataset version."""

    dataset_id: str
    version: str
    path: str | Path
    description: str = ""
    splits: dict[str, DatasetSplit] | None = None
    tags: dict[str, str] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    source_url: str | None = None
    source_hash: str | None = None


class DatasetRegistry:
    """Dataset registry backed by DuckDB."""

    def __init__(
        self,
        conn: duckdb.DuckDBPyConnection,
        write_lock: Any,
        data_root: Path | str = "data/datasets",
    ) -> None:
        self._conn = conn
        self._write_lock = write_lock
        self._data_root = Path(data_root)
        self._data_root.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def _init_schema(self) -> None:
        """Initialize the dataset registry schema."""
        with self._write_lock:
            self._conn.execute("""
                CREATE TABLE IF NOT EXISTS dataset_registry (
                    dataset_id VARCHAR NOT NULL,
                    version VARCHAR NOT NULL,
                    digest VARCHAR NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    description VARCHAR DEFAULT '',
                    splits JSON,
                    tags JSON,
                    metadata JSON,
                    source_url VARCHAR,
                    source_hash VARCHAR,
                    PRIMARY KEY (dataset_id, version)
                )
            """)
            self._conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_dataset_registry_dataset_id
                ON dataset_registry(dataset_id)
            """)

    def _compute_digest(self, path: Path) -> str:
        """Compute SHA256 digest of a file or directory."""
        hasher = hashlib.sha256()

        if path.is_file():
            with path.open("rb") as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    hasher.update(chunk)
        else:
            # For directories, hash all files in sorted order
            for file_path in sorted(path.rglob("*")):
                if file_path.is_file():
                    rel_path = file_path.relative_to(path)
                    hasher.update(str(rel_path).encode())
                    with file_path.open("rb") as f:
                        for chunk in iter(lambda: f.read(8192), b""):
                            hasher.update(chunk)

        return hasher.hexdigest()

    def _compute_file_hash(self, path: Path) -> str:
        """Compute SHA256 of a single file."""
        hasher = hashlib.sha256()
        with path.open("rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                hasher.update(chunk)
        return hasher.hexdigest()

    def register(self, registration: DatasetRegistration) -> DatasetVersion:
        """Register a dataset version from a directory."""
        path = Path(registration.path)
        if not path.exists():
            raise FileNotFoundError(f"Dataset not found: {path}")

        digest = self._compute_digest(path)

        # Auto-detect splits if not provided
        splits = registration.splits or {}
        if not splits:
            splits = self._detect_splits(path)

        version = DatasetVersion(
            dataset_id=registration.dataset_id,
            version=registration.version,
            digest=digest,
            created_at=datetime.now().isoformat(),
            description=registration.description,
            splits=splits,
            tags=registration.tags,
            metadata=registration.metadata,
            source_url=registration.source_url,
            source_hash=registration.source_hash,
        )

        with self._write_lock:
            self._conn.execute(
                """
                INSERT INTO dataset_registry (
                    dataset_id, version, digest, created_at, description,
                    splits, tags, metadata, source_url, source_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT (dataset_id, version) DO UPDATE SET
                    digest=excluded.digest,
                    created_at=excluded.created_at,
                    description=excluded.description,
                    splits=excluded.splits,
                    tags=excluded.tags,
                    metadata=excluded.metadata,
                    source_url=excluded.source_url,
                    source_hash=excluded.source_hash
                """,
                [
                    version.dataset_id,
                    version.version,
                    version.digest,
                    version.created_at,
                    version.description,
                    json.dumps({
                        k: {
                            "name": v.name,
                            "path": v.path,
                            "hash": v.hash,
                            "size_bytes": v.size_bytes,
                            "num_samples": v.num_samples,
                            "metadata": v.metadata,
                        }
                        for k, v in version.splits.items()
                    }),
                    json.dumps(version.tags),
                    json.dumps(version.metadata),
                    version.source_url,
                    version.source_hash,
                ],
            )

        logger.info(
            "Registered dataset %s version %s (digest: %s...)",
            version.dataset_id,
            version.version,
            version.digest[:12],
        )
        return version

    def _detect_splits(self, path: Path) -> dict[str, DatasetSplit]:
        """Auto-detect standard splits (train/val/test)."""
        splits = {}
        for split_name in ["train", "val", "validation", "test"]:
            split_path = path / split_name
            if split_path.exists() and split_path.is_dir():
                file_count = sum(1 for _ in split_path.rglob("*") if _.is_file())
                if file_count > 0:
                    split_hash = self._compute_digest(split_path)
                    splits[split_name] = DatasetSplit(
                        name=split_name,
                        path=str(split_path.relative_to(path)),
                        hash=split_hash,
                        size_bytes=sum(
                            f.stat().st_size
                            for f in split_path.rglob("*")
                            if f.is_file()
                        ),
                        num_samples=file_count,
                    )
        return splits

    def get(self, dataset_id: str, version: str) -> DatasetVersion | None:
        """Get a dataset version."""
        row = self._conn.execute(
            "SELECT * FROM dataset_registry WHERE dataset_id = ? AND version = ?",
            [dataset_id, version],
        ).fetchone()
        if not row:
            return None
        return self._row_to_version(row)

    def get_latest(self, dataset_id: str) -> DatasetVersion | None:
        """Get the latest version of a dataset."""
        row = self._conn.execute(
            "SELECT * FROM dataset_registry WHERE dataset_id = ? ORDER BY created_at DESC LIMIT 1",
            [dataset_id],
        ).fetchone()
        if not row:
            return None
        return self._row_to_version(row)

    def list_versions(self, dataset_id: str) -> list[DatasetVersion]:
        """List all versions of a dataset."""
        rows = self._conn.execute(
            "SELECT * FROM dataset_registry WHERE dataset_id = ? ORDER BY created_at DESC",
            [dataset_id],
        ).fetchall()
        return [self._row_to_version(row) for row in rows]

    def list_datasets(
        self,
        tag_filter: dict[str, str] | None = None,
        limit: int = 100,
    ) -> list[DatasetVersion]:
        """List datasets with optional tag filters."""
        query = "SELECT * FROM dataset_registry WHERE 1=1"
        params: list[Any] = []

        if tag_filter:
            for key, value in tag_filter.items():
                query += " AND json_extract(tags, ?) = ?"
                params.extend([f"$.{key}", value])

        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)

        rows = self._conn.execute(query, params).fetchall()
        return [self._row_to_version(row) for row in rows]

    def verify_integrity(self, dataset_id: str, version: str) -> dict[str, Any]:
        """Verify dataset integrity by recomputing hashes."""
        version_obj = self.get(dataset_id, version)
        if not version_obj:
            return {"valid": False, "error": "Dataset not found"}

        # Find the dataset directory
        dataset_path = self._data_root / dataset_id / version
        if not dataset_path.exists():
            return {"valid": False, "error": f"Dataset path not found: {dataset_path}"}

        # Verify overall digest
        current_digest = self._compute_digest(dataset_path)
        overall_valid = current_digest == version_obj.digest

        # Verify splits
        split_results = {}
        for split_name, split_info in version_obj.splits.items():
            split_path = dataset_path / split_info.path
            if split_path.exists():
                current_split_hash = self._compute_digest(split_path)
                split_results[split_name] = {
                    "valid": current_split_hash == split_info.hash,
                    "expected_hash": split_info.hash,
                    "actual_hash": current_split_hash,
                }
            else:
                split_results[split_name] = {
                    "valid": False,
                    "error": f"Split path not found: {split_path}",
                }

        return {
            "valid": overall_valid
            and all(r.get("valid", False) for r in split_results.values()),
            "overall_digest": {
                "expected": version_obj.digest,
                "actual": current_digest,
                "valid": overall_valid,
            },
            "splits": split_results,
        }

    def export_metadata(self, dataset_id: str, version: str, output_path: Path) -> Path:
        """Export dataset metadata to JSON."""
        version_obj = self.get(dataset_id, version)
        if not version_obj:
            raise ValueError(f"Dataset {dataset_id} version {version} not found")

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(
                {
                    "dataset_id": version_obj.dataset_id,
                    "version": version_obj.version,
                    "digest": version_obj.digest,
                    "created_at": version_obj.created_at,
                    "description": version_obj.description,
                    "splits": {
                        k: {
                            "name": v.name,
                            "path": v.path,
                            "hash": v.hash,
                            "size_bytes": v.size_bytes,
                            "num_samples": v.num_samples,
                            "metadata": v.metadata,
                        }
                        for k, v in version_obj.splits.items()
                    },
                    "tags": version_obj.tags,
                    "metadata": version_obj.metadata,
                    "source_url": version_obj.source_url,
                    "source_hash": version_obj.source_hash,
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        return output_path

    def _row_to_version(self, row: tuple) -> DatasetVersion:
        """Convert database row to DatasetVersion."""
        (
            dataset_id,
            version,
            digest,
            created_at,
            description,
            splits_json,
            tags_json,
            metadata_json,
            source_url,
            source_hash,
        ) = row

        splits = {}
        if splits_json:
            for k, v in json.loads(splits_json).items():
                splits[k] = DatasetSplit(**v)

        return DatasetVersion(
            dataset_id=dataset_id,
            version=version,
            digest=digest,
            created_at=created_at,
            description=description,
            splits=splits,
            tags=json.loads(tags_json) if tags_json else {},
            metadata=json.loads(metadata_json) if metadata_json else {},
            source_url=source_url,
            source_hash=source_hash,
        )


def get_git_sha() -> str | None:
    """Get the current git commit SHA."""
    try:
        import shutil

        git_path = shutil.which("git")
        if not git_path:
            return None
        return subprocess.check_output(  # ruff: ignore[start-process-with-partial-path, subprocess-without-shell-equals-true]
            [git_path, "rev-parse", "HEAD"],
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
    except Exception:
        return None


def create_dataset_manifest(
    dataset_path: Path,
    dataset_id: str,
    version: str,
    description: str = "",
) -> DatasetRegistration:
    """Create a dataset registration from a directory structure."""
    return DatasetRegistration(
        dataset_id=dataset_id,
        version=version,
        path=dataset_path,
        description=description,
    )


__all__ = [
    "DatasetRegistration",
    "DatasetRegistry",
    "DatasetSplit",
    "DatasetVersion",
    "create_dataset_manifest",
    "get_git_sha",
]
