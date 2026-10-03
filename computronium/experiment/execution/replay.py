"""Replay: the run-level identity hash (WP4).

RETIRED (D3, TODO48): the JSON checkpoint/resume subsystem this module also
carried — ``Checkpoint``, ``create_checkpoint``, ``periodic_checkpoint``,
``resume_from_store``, ``resume_run``, ``ResumeResult``, ``find_existing_record``
— is deleted with a record, not with a shrug. It had zero production readers:
``comp run`` wrote one file per round and resumed from the store, so every file
was a duplicate of evidence the store already held, growing with the round
count on exactly the long campaigns that need their disk. A cell-level
checkpoint that a crashed round restarts from is the per-cell resume TODO47 §5
warns against, because the seeds it holds are the ones whose rounds were
already spent. The store *is* the checkpoint: it survives the process, and
``comp run --run-id <id>`` continues from it for every policy, because the
proposal stream is filtered by the run's own measured keys.
"""

from __future__ import annotations

import hashlib
import json
import logging
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Iterable

    from computronium.experiment.schema.run_spec import RunSpec


logger = logging.getLogger(__name__)


def _canonical_json(obj: Any) -> str:
    """Serialize to canonical JSON for hashing."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


# RETIRED (Q8, TODO48): Per-cell replay hash is not used in production.
# The run-level compute_run_replay_hash is the gate. This function had
# zero production callers. Kept for reference only.
# def compute_replay_hash(
#     coordinate: Coordinate,
#     schedule: Schedule,
#     provenance: dict[str, Any],
#     params: dict[str, Any],
# ) -> str:
#     ...


def compute_run_replay_hash(
    run_spec: RunSpec,
    measurement_keys: Iterable[str],
) -> str:
    """Compute the run-level replay hash: what this run declared, and what it measured.

    A per-cell :func:`compute_replay_hash` cannot detect a *diverged* run — it
    says nothing about which cells the run actually visited. This one covers the
    whole declaration plus the sorted set of ``measurement_key``\\ s the run
    measured, so a run that measured a different set of cells hashes differently
    from the run it claims to replay.

    Measured *values* are deliberately excluded: walltime and float kernels are
    not reproducible, so including them would make the hash a fingerprint of one
    execution rather than of the run's identity.

    Args:
        run_spec: The run's declaration.
        measurement_keys: Every ``measurement_key`` the run measured.

    Returns:
        SHA256 hash as hex string (64 chars).
    """
    replay_data = {
        "spec": run_spec.to_dict(),
        "measured": sorted(set(measurement_keys)),
    }
    return hashlib.sha256(_canonical_json(replay_data).encode()).hexdigest()


__all__ = ["compute_run_replay_hash"]
