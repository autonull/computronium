"""Unified ExperimentRegistry: thin unification of store + state + ledger.

Provides the single integration seam for the experiment loop.
Combines RecordStore, provenance, seeds, and checkpoints into one API.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path  # ruff: ignore[typing-only-standard-library-import]
from typing import Any, Self

from computronium.experiment.evidence.store import RecordStore, StoreConfig
from computronium.experiment.registry.checkpoint import (
    CheckpointManager,
    compute_spec_hash,
)
from computronium.experiment.registry.provenance import (
    ProvenanceBuilder,
    ProvenanceRecord,
    validate_provenance,
)
from computronium.experiment.registry.seed import SeedContext, SeedContextManager
from computronium.experiment.schema.run_spec import RunSpec  # ruff: ignore[typing-only-first-party-import]

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class ExperimentConfig:
    """Configuration for the unified experiment registry."""

    store_path: Path
    run_id: str | None = None
    spec: RunSpec | None = None
    master_seed: int | None = None
    read_only: bool = False


class ExperimentRegistry:
    """Single integration point for all experiment state.

    Unifies:
    - RecordStore (evidence storage)
    - ProvenanceBuilder (immutable provenance per record)
    - SeedContextManager (deterministic seed hierarchy)
    - CheckpointManager (transactional cycle commits)
    """

    def __init__(self, config: ExperimentConfig) -> None:
        self._config = config
        self._store: RecordStore | None = None
        self._provenance: ProvenanceBuilder | None = None
        self._seeds: SeedContextManager | None = None
        self._checkpoints: CheckpointManager | None = None
        self._spec_hash: str | None = None

    def __enter__(self) -> Self:
        self._store = RecordStore(
            StoreConfig(path=self._config.store_path, read_only=self._config.read_only)
        )
        self._store.__enter__()

        if not self._config.read_only and self._config.spec is not None:
            self._spec_hash = compute_spec_hash(self._config.spec.to_dict())
            run_id = self._config.run_id or self._store.create_run(
                spec=self._config.spec
            )

            # Initialize provenance
            seed_list = self._collect_all_seeds(self._config.spec)
            task_versions = dict.fromkeys(self._config.spec.task_names, "1.0")
            self._provenance = ProvenanceBuilder(
                run_id=run_id,
                config_sha256=self._spec_hash,
                seed_list=tuple(seed_list),
                task_versions=task_versions,
            )

            # Initialize seeds
            self._seeds = SeedContextManager(master_seed=self._config.master_seed)

            # Initialize checkpoints
            self._checkpoints = CheckpointManager(self._store, run_id, self._spec_hash)

        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if self._store is not None:
            self._store.__exit__(exc_type, exc_val, exc_tb)

    @property
    def store(self) -> RecordStore:
        if self._store is None:
            raise RuntimeError("Registry not initialized (use 'with' context)")
        return self._store

    @property
    def provenance(self) -> ProvenanceBuilder:
        if self._provenance is None:
            raise RuntimeError("Provenance not initialized (read-only mode?)")
        return self._provenance

    @property
    def seeds(self) -> SeedContextManager:
        if self._seeds is None:
            raise RuntimeError("Seeds not initialized (read-only mode?)")
        return self._seeds

    @property
    def checkpoints(self) -> CheckpointManager:
        if self._checkpoints is None:
            raise RuntimeError("Checkpoints not initialized (read-only mode?)")
        return self._checkpoints

    @property
    def run_id(self) -> str:
        if self._provenance is None:
            raise RuntimeError("Registry not initialized")
        return self._provenance.run_id

    @property
    def spec_hash(self) -> str:
        if self._spec_hash is None:
            raise RuntimeError("Spec hash not computed")
        return self._spec_hash

    def _collect_all_seeds(self, spec: RunSpec) -> list[int]:
        """Collect all seeds the run will use across all cells and cycles."""
        # For now, return the base seed plan
        # In practice this would be expanded based on the search space
        base_seed = self._config.master_seed or spec.seed
        return [base_seed + i for i in range(spec.n_seeds * 10)]  # Estimate

    def write_record_with_provenance(self, record: Any) -> Any:
        """Write a record with enforced provenance.

        Validates provenance before write; fails if incomplete.
        """
        store = self.store  # Raises if not initialized
        provenance = self.provenance  # Raises if not initialized

        prov_record = provenance.build()
        validate_provenance(prov_record)

        # The record already carries provenance via its schema.Provenance field.
        # Here we ensure the store write happens with all checks.
        return store.append(record)

    def start_cycle(self, cycle_index: int) -> None:
        """Start a new cycle."""
        checkpoints = self.checkpoints  # Raises if not initialized
        seeds = self.seeds  # Raises if not initialized
        checkpoints.start_cycle(cycle_index)
        seeds.next_cycle()

    def complete_cell(self, measurement_key: str) -> None:
        """Mark a cell as completed in the current cycle."""
        checkpoints = self.checkpoints  # Raises if not initialized
        checkpoints.record_cell_completed(measurement_key)

    def commit_cycle(self, budget_consumed_s: float) -> Any:
        """Commit the current cycle atomically."""
        checkpoints = self.checkpoints  # Raises if not initialized
        return checkpoints.commit_cycle(budget_consumed_s)

    def get_resume_point(self) -> tuple[int, list[str]] | None:
        """Get resume point after crash: (next_cycle, completed_cells)."""
        checkpoints = self.checkpoints  # Raises if not initialized
        return checkpoints.get_resume_point()


def create_registry(config: ExperimentConfig) -> ExperimentRegistry:
    """Factory for ExperimentRegistry."""
    return ExperimentRegistry(config)


__all__ = [
    "ExperimentConfig",
    "ExperimentRegistry",
    "ProvenanceRecord",
    "SeedContext",
    "create_registry",
]
