"""Model Registry: Versioned checkpoints with metadata.

Extends the artifact store to provide a model registry with:
- Semantic versioning for model checkpoints
- Model metadata (architecture, hyperparameters, metrics)
- Lineage tracking (parent models, training runs)
- Model promotion (staging → production)
- Search and filtering by metrics, tags, etc.
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

    from computronium.experiment.schema.record import Record

from computronium.experiment.evidence.artifacts import ArtifactInput, ArtifactRole

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class ModelVersion:
    """A versioned model checkpoint."""

    model_id: str
    version: str  # Semantic version (e.g., "1.0.0", "1.1.0-rc1")
    digest: str  # SHA256 of checkpoint
    created_at: str
    # Metadata
    coordinate: dict[str, Any] | None = None  # 6-axis coordinate
    metrics: dict[str, float] = field(default_factory=dict)
    hyperparameters: dict[str, Any] = field(default_factory=dict)
    tags: dict[str, str] = field(default_factory=dict)
    # Lineage
    parent_version: str | None = None
    training_run_id: str | None = None
    # Status
    stage: str = "development"  # development, staging, production, archived
    description: str = ""


@dataclass(frozen=True, slots=True)
class ModelRegistration:
    """Input for registering a model version."""

    model_id: str
    version: str
    checkpoint_path: str | Path
    coordinate: dict[str, Any] | None = None
    metrics: dict[str, float] = field(default_factory=dict)
    hyperparameters: dict[str, Any] = field(default_factory=dict)
    tags: dict[str, str] = field(default_factory=dict)
    parent_version: str | None = None
    training_run_id: str | None = None
    stage: str = "development"
    description: str = ""


class ModelRegistry:
    """Model registry backed by DuckDB artifacts table."""

    def __init__(
        self,
        conn: duckdb.DuckDBPyConnection,
        write_lock: Any,  # threading.Lock
        artifact_store: Any,  # ArtifactStore
    ) -> None:
        self._conn = conn
        self._write_lock = write_lock
        self._artifact_store = artifact_store
        self._init_schema()

    def _init_schema(self) -> None:
        """Initialize the model registry schema."""
        with self._write_lock:
            self._conn.execute("""
                CREATE TABLE IF NOT EXISTS model_registry (
                    model_id VARCHAR NOT NULL,
                    version VARCHAR NOT NULL,
                    digest VARCHAR NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    coordinate JSON,
                    metrics JSON,
                    hyperparameters JSON,
                    tags JSON,
                    parent_version VARCHAR,
                    training_run_id VARCHAR,
                    stage VARCHAR DEFAULT 'development',
                    description VARCHAR DEFAULT '',
                    PRIMARY KEY (model_id, version)
                )
            """)
            self._conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_model_registry_model_id
                ON model_registry(model_id)
            """)
            self._conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_model_registry_stage
                ON model_registry(stage)
            """)
            self._conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_model_registry_metric
                ON model_registry(metrics)
            """)

    def _compute_digest(self, path: Path) -> str:
        """Compute SHA256 digest of a file."""
        hasher = hashlib.sha256()
        with path.open("rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                hasher.update(chunk)
        return hasher.hexdigest()

    def register(self, registration: ModelRegistration) -> ModelVersion:
        """Register a model version from a checkpoint file."""
        path = Path(registration.checkpoint_path)
        if not path.exists():
            raise FileNotFoundError(f"Checkpoint not found: {path}")

        digest = self._compute_digest(path)

        # Store checkpoint as artifact
        artifact_input = ArtifactInput(
            bytes=path.read_bytes(),
            role=ArtifactRole.MODEL_CHECKPOINT,
            digest=digest,
        )
        self._artifact_store.put(
            artifact_input, f"model_{registration.model_id}_{registration.version}"
        )

        version = ModelVersion(
            model_id=registration.model_id,
            version=registration.version,
            digest=digest,
            created_at=datetime.now().isoformat(),
            coordinate=registration.coordinate,
            metrics=registration.metrics,
            hyperparameters=registration.hyperparameters,
            tags=registration.tags,
            parent_version=registration.parent_version,
            training_run_id=registration.training_run_id,
            stage=registration.stage,
            description=registration.description,
        )

        with self._write_lock:
            self._conn.execute(
                """
                INSERT INTO model_registry (
                    model_id, version, digest, created_at, coordinate,
                    metrics, hyperparameters, tags, parent_version,
                    training_run_id, stage, description
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT (model_id, version) DO UPDATE SET
                    digest=excluded.digest,
                    created_at=excluded.created_at,
                    coordinate=excluded.coordinate,
                    metrics=excluded.metrics,
                    hyperparameters=excluded.hyperparameters,
                    tags=excluded.tags,
                    parent_version=excluded.parent_version,
                    training_run_id=excluded.training_run_id,
                    stage=excluded.stage,
                    description=excluded.description
                """,
                [
                    version.model_id,
                    version.version,
                    version.digest,
                    version.created_at,
                    json.dumps(version.coordinate) if version.coordinate else None,
                    json.dumps(version.metrics),
                    json.dumps(version.hyperparameters),
                    json.dumps(version.tags),
                    version.parent_version,
                    version.training_run_id,
                    version.stage,
                    version.description,
                ],
            )

        logger.info(
            "Registered model %s version %s (digest: %s...)",
            version.model_id,
            version.version,
            version.digest[:12],
        )
        return version

    def register_from_record(
        self,
        record: Record,
        model_id: str,
        version: str,
        stage: str = "development",
        description: str = "",
    ) -> ModelVersion:
        """Register a model from a completed experiment record."""
        # Extract checkpoint from record artifacts
        artifacts = self._artifact_store.get_for_record(record.record_id)
        checkpoint_artifact = None
        for artifact in artifacts:
            if artifact.role == ArtifactRole.MODEL_CHECKPOINT:
                checkpoint_artifact = artifact
                break

        if not checkpoint_artifact:
            raise ValueError(
                f"No checkpoint artifact found for record {record.record_id}"
            )

        # Extract coordinate and metrics from record
        coordinate = None
        if hasattr(record, "coordinate") and record.coordinate:
            coordinate = record.coordinate.to_dict()
        metrics = {
            k: float(v) for k, v in record.payload.items() if isinstance(v, int | float)
        }

        # Create temp file for checkpoint
        import tempfile

        temp_path = None
        artifact_bytes = self._artifact_store.get(checkpoint_artifact.digest)
        if artifact_bytes:
            with tempfile.NamedTemporaryFile(suffix=".pt", delete=False) as f:
                f.write(artifact_bytes)
                temp_path = f.name

        # Create registration
        registration = ModelRegistration(
            model_id=model_id,
            version=version,
            checkpoint_path=temp_path or "",
            coordinate=coordinate,
            metrics=metrics,
            hyperparameters=record.effective_params or {},
            training_run_id=record.provenance.links.get("run_id"),
            stage=stage,
            description=description,
        )

        return self.register(registration)

    def get(self, model_id: str, version: str) -> ModelVersion | None:
        """Get a model version."""
        row = self._conn.execute(
            "SELECT * FROM model_registry WHERE model_id = ? AND version = ?",
            [model_id, version],
        ).fetchone()
        if not row:
            return None
        return self._row_to_version(row)

    def get_latest(
        self, model_id: str, stage: str | None = None
    ) -> ModelVersion | None:
        """Get the latest version of a model, optionally filtered by stage."""
        query = "SELECT * FROM model_registry WHERE model_id = ?"
        params: list[Any] = [model_id]
        if stage:
            query += " AND stage = ?"
            params.append(stage)
        query += " ORDER BY created_at DESC LIMIT 1"

        row = self._conn.execute(query, params).fetchone()
        if not row:
            return None
        return self._row_to_version(row)

    def get_production(self, model_id: str) -> ModelVersion | None:
        """Get the production version of a model."""
        return self.get_latest(model_id, stage="production")

    def list_versions(self, model_id: str) -> list[ModelVersion]:
        """List all versions of a model."""
        rows = self._conn.execute(
            "SELECT * FROM model_registry WHERE model_id = ? ORDER BY created_at DESC",
            [model_id],
        ).fetchall()
        return [self._row_to_version(row) for row in rows]

    def list_models(
        self,
        stage: str | None = None,
        tag_filter: dict[str, str] | None = None,
        metric_filter: dict[str, tuple[float, float]] | None = None,
        limit: int = 100,
    ) -> list[ModelVersion]:
        """List models with optional filters."""
        query = "SELECT * FROM model_registry WHERE 1=1"
        params: list[Any] = []

        if stage:
            query += " AND stage = ?"
            params.append(stage)

        if tag_filter:
            for key, value in tag_filter.items():
                query += " AND json_extract(tags, ?) = ?"
                params.extend([f"$.{key}", value])

        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)

        rows = self._conn.execute(query, params).fetchall()
        versions = [self._row_to_version(row) for row in rows]

        # Post-filter by metrics (DuckDB JSON filtering is limited)
        if metric_filter:
            filtered = []
            for v in versions:
                match = True
                for metric, (min_val, max_val) in metric_filter.items():
                    val = v.metrics.get(metric)
                    if val is None or val < min_val or val > max_val:
                        match = False
                        break
                if match:
                    filtered.append(v)
            return filtered

        return versions

    def promote(self, model_id: str, version: str, stage: str) -> bool:
        """Promote a model version to a new stage."""
        valid_stages = {"development", "staging", "production", "archived"}
        if stage not in valid_stages:
            raise ValueError(f"Invalid stage: {stage}. Must be one of {valid_stages}")

        with self._write_lock:
            result = self._conn.execute(
                "UPDATE model_registry SET stage = ? WHERE model_id = ? AND version = ?",
                [stage, model_id, version],
            )
            return result.rowcount > 0

    def add_tag(self, model_id: str, version: str, key: str, value: str) -> bool:
        """Add a tag to a model version."""
        version_obj = self.get(model_id, version)
        if not version_obj:
            return False

        tags = dict(version_obj.tags)
        tags[key] = value

        with self._write_lock:
            self._conn.execute(
                "UPDATE model_registry SET tags = ? WHERE model_id = ? AND version = ?",
                [json.dumps(tags), model_id, version],
            )
        return True

    def download_checkpoint(
        self, model_id: str, version: str, output_path: Path
    ) -> Path:
        """Download a model checkpoint to a local path."""
        version_obj = self.get(model_id, version)
        if not version_obj:
            raise ValueError(f"Model {model_id} version {version} not found")

        # Get artifact bytes
        bytes_data = self._artifact_store.get(version_obj.digest)
        if not bytes_data:
            raise ValueError(f"Checkpoint data not found for {model_id} v{version}")

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(bytes_data)
        return output_path

    def _row_to_version(self, row: tuple) -> ModelVersion:
        """Convert database row to ModelVersion."""
        (
            model_id,
            version,
            digest,
            created_at,
            coordinate_json,
            metrics_json,
            hyperparameters_json,
            tags_json,
            parent_version,
            training_run_id,
            stage,
            description,
        ) = row

        return ModelVersion(
            model_id=model_id,
            version=version,
            digest=digest,
            created_at=created_at,
            coordinate=json.loads(coordinate_json) if coordinate_json else None,
            metrics=json.loads(metrics_json) if metrics_json else {},
            hyperparameters=json.loads(hyperparameters_json)
            if hyperparameters_json
            else {},
            tags=json.loads(tags_json) if tags_json else {},
            parent_version=parent_version,
            training_run_id=training_run_id,
            stage=stage,
            description=description,
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


__all__ = [
    "ModelRegistration",
    "ModelRegistry",
    "ModelVersion",
    "get_git_sha",
]
