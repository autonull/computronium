"""Provenance contract: every record carries immutable provenance metadata.

Enforces that all records include: run_id, code_git_sha, config_sha256,
seed_list, env_fingerprint, task_versions, hardware_hash.
A record without provenance fails to commit.
"""

from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from computronium.experiment.environment.snapshots import EnvironmentSnapshot

from computronium.core.utils.git import git_sha
from computronium.experiment.environment.snapshots import (
    EnvironmentCapture,
    EnvironmentSnapshot,
)
from computronium.experiment.schema.coordinate import Provenance as SchemaProvenance

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class ProvenanceRecord:
    """Complete, immutable provenance for a single record.

    This is what gets written to the store alongside every record.
    All fields are required; missing fields cause write failure.
    """

    run_id: str
    code_git_sha: str
    config_sha256: str
    seed_list: tuple[int, ...]
    env_fingerprint: str  # SHA256 of EnvironmentSnapshot
    task_versions: dict[str, str]  # task_name -> dataset_version
    hardware_hash: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "code_git_sha": self.code_git_sha,
            "config_sha256": self.config_sha256,
            "seed_list": list(self.seed_list),
            "env_fingerprint": self.env_fingerprint,
            "task_versions": self.task_versions,
            "hardware_hash": self.hardware_hash,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ProvenanceRecord:
        return cls(
            run_id=data["run_id"],
            code_git_sha=data["code_git_sha"],
            config_sha256=data["config_sha256"],
            seed_list=tuple(data["seed_list"]),
            env_fingerprint=data["env_fingerprint"],
            task_versions=data["task_versions"],
            hardware_hash=data["hardware_hash"],
        )


class ProvenanceBuilder:
    """Builds ProvenanceRecord from the current execution context.

    Captures all required fields at the start of a run/cycle and
    provides them for every record written during that cycle.
    """

    def __init__(
        self,
        run_id: str,
        config_sha256: str,
        seed_list: tuple[int, ...],
        task_versions: dict[str, str] | None = None,
        env_snapshot: EnvironmentSnapshot | None = None,
    ) -> None:
        self.run_id = run_id
        self.code_git_sha = git_sha() or "unknown"
        self.config_sha256 = config_sha256
        self.seed_list = seed_list
        self.task_versions = task_versions or {}
        self.env_snapshot = env_snapshot or EnvironmentCapture().capture()
        self._env_fingerprint: str | None = None
        self._hardware_hash: str | None = None

    @property
    def env_fingerprint(self) -> str:
        """SHA256 of the environment snapshot."""
        if self._env_fingerprint is None:
            snap_json = self.env_snapshot.to_json()
            self._env_fingerprint = hashlib.sha256(snap_json.encode()).hexdigest()
        return self._env_fingerprint

    @property
    def hardware_hash(self) -> str:
        """Hardware fingerprint from system snapshot."""
        if self._hardware_hash is None:
            hw_data = {
                "platform": self.env_snapshot.system.platform,
                "architecture": self.env_snapshot.system.architecture,
                "cpu_count": self.env_snapshot.system.cpu_count,
                "memory_gb": self.env_snapshot.system.memory_gb,
                "gpu_info": self.env_snapshot.system.gpu_info,
                "cuda_version": self.env_snapshot.system.cuda_version,
            }
            hw_json = json.dumps(hw_data, sort_keys=True)
            self._hardware_hash = hashlib.sha256(hw_json.encode()).hexdigest()
        return self._hardware_hash

    def build(self) -> ProvenanceRecord:
        """Build the complete ProvenanceRecord."""
        return ProvenanceRecord(
            run_id=self.run_id,
            code_git_sha=self.code_git_sha,
            config_sha256=self.config_sha256,
            seed_list=self.seed_list,
            env_fingerprint=self.env_fingerprint,
            task_versions=self.task_versions,
            hardware_hash=self.hardware_hash,
        )

    def to_schema_provenance(self) -> SchemaProvenance:
        """Convert to the schema's Provenance for record storage."""
        return SchemaProvenance(
            env=dict(self.env_snapshot.environment_variables),
            dataset=self.task_versions.get("primary", "unknown"),
            dataset_version=next(iter(self.task_versions.values()), "1.0"),
            code_sha=self.code_git_sha,
            policy="unknown",  # Will be filled by caller
            links={"run_id": self.run_id},
        )


def validate_provenance(provenance: ProvenanceRecord) -> None:
    """Validate that a ProvenanceRecord has all required fields.

    Raises:
        ValueError: If any required field is missing or empty.
    """
    required = [
        "run_id",
        "code_git_sha",
        "config_sha256",
        "seed_list",
        "env_fingerprint",
        "task_versions",
        "hardware_hash",
    ]
    for field_name in required:
        value = getattr(provenance, field_name)
        if value is None or (isinstance(value, str | tuple | dict) and not value):
            raise ValueError(f"ProvenanceRecord missing required field: {field_name}")

    # Ensure seed_list is non-empty
    if len(provenance.seed_list) == 0:
        raise ValueError("ProvenanceRecord.seed_list must be non-empty")


def compute_config_sha256(config: dict[str, Any]) -> str:
    """Compute SHA256 of a configuration dict."""
    canonical = json.dumps(config, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode()).hexdigest()


__all__ = [
    "ProvenanceBuilder",
    "ProvenanceRecord",
    "compute_config_sha256",
    "validate_provenance",
]
