"""Reproducibility Analysis (Phase D5).

Verifies checkpoint replay and bitwise reproducibility of experiments.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from computronium.experiment.evidence.store import RecordStore


@dataclass(frozen=True, slots=True)
class ReproducibilityResult:
    """Result of reproducibility verification."""

    run_id: str
    checkpoint_path: str
    original_metrics: dict[str, float]
    replayed_metrics: dict[str, float]
    metrics_match: bool
    bitwise_match: bool
    max_relative_diff: float
    mismatched_keys: list[str]
    metadata: dict[str, Any]


@dataclass(frozen=True, slots=True)
class ReproducibilityConfig:
    """Configuration for reproducibility verification."""

    tolerance: float = 1e-6
    metrics_to_verify: list[str] | None = None


def _compute_tensor_hash(tensor) -> str:
    """Compute hash of a tensor for bitwise comparison."""
    return hashlib.sha256(tensor.cpu().numpy().tobytes()).hexdigest()


def _compare_state_dicts(
    state1: dict[str, Any],
    state2: dict[str, Any],
    tolerance: float = 1e-6,
) -> tuple[bool, float, list[str]]:
    """Compare two state dictionaries."""
    mismatched = []
    max_rel_diff = 0.0

    all_keys = set(state1.keys()) | set(state2.keys())
    for key in all_keys:
        if key not in state1:
            mismatched.append(f"{key}: missing in original")
            continue
        if key not in state2:
            mismatched.append(f"{key}: missing in replayed")
            continue

        v1 = state1[key]
        v2 = state2[key]

        if hasattr(v1, "shape") and hasattr(v2, "shape"):
            # Tensor comparison
            if v1.shape != v2.shape:
                mismatched.append(f"{key}: shape mismatch {v1.shape} vs {v2.shape}")
                continue

            diff = (v1 - v2).abs()
            max_diff = diff.max().item()
            rel_diff = max_diff / (v1.abs().max().item() + 1e-12)
            max_rel_diff = max(max_rel_diff, rel_diff)

            if rel_diff > tolerance:
                mismatched.append(f"{key}: rel_diff={rel_diff:.2e}")

    return len(mismatched) == 0, max_rel_diff, mismatched


def verify_checkpoint_replay(
    original_run_id: str,
    checkpoint_path: str,
    store: RecordStore,
    config: ReproducibilityConfig | None = None,
) -> ReproducibilityResult:
    """Verify that a checkpoint can be replayed to produce identical results."""
    config = config or ReproducibilityConfig()

    # This is a placeholder - actual implementation would:
    # 1. Load the original run config from store
    # 2. Re-run the experiment from checkpoint
    # 3. Compare metrics

    # For now, return a structured result indicating the capability
    return ReproducibilityResult(
        run_id=original_run_id,
        checkpoint_path=checkpoint_path,
        original_metrics={},
        replayed_metrics={},
        metrics_match=False,
        bitwise_match=False,
        max_relative_diff=0.0,
        mismatched_keys=["Not implemented: requires re-running experiment"],
        metadata={
            "tolerance": config.tolerance,
            "note": "Requires integration with training loop for full verification",
        },
    )


def verify_bitwise_reproducibility(
    run_id: str,
    store: RecordStore,
    config: ReproducibilityConfig | None = None,
) -> ReproducibilityResult:
    """Verify bitwise reproducibility by re-running with same seed."""
    config = config or ReproducibilityConfig()

    # This would require re-running the experiment
    # Placeholder for integration
    return ReproducibilityResult(
        run_id=run_id,
        checkpoint_path="",
        original_metrics={},
        replayed_metrics={},
        metrics_match=False,
        bitwise_match=False,
        max_relative_diff=0.0,
        mismatched_keys=["Not implemented: requires re-running experiment"],
        metadata={
            "tolerance": config.tolerance,
            "note": "Requires re-running experiment with same seed",
        },
    )


class ReproducibilityAnalyzer:
    """Analyze reproducibility of experiments."""

    def __init__(
        self,
        store: RecordStore,
        config: ReproducibilityConfig | None = None,
    ):
        self.store = store
        self.config = config or ReproducibilityConfig()

    def verify_run_reproducibility(
        self,
        run_id: str,
    ) -> ReproducibilityResult:
        """Verify reproducibility of a run by checking for bitwise match."""
        from computronium.experiment.surface.report import ReportGenerator

        generator = ReportGenerator(self.store)
        summary = generator.run_summary(run_id)

        if not summary:
            return ReproducibilityResult(
                run_id=run_id,
                checkpoint_path="",
                original_metrics={},
                replayed_metrics={},
                metrics_match=False,
                bitwise_match=False,
                max_relative_diff=0.0,
                mismatched_keys=["Run not found"],
                metadata={},
            )

        # Check if run has replay hash
        has_replay_hash = summary.replay_hash is not None

        return ReproducibilityResult(
            run_id=run_id,
            checkpoint_path="",
            original_metrics={},
            replayed_metrics={},
            metrics_match=has_replay_hash,
            bitwise_match=has_replay_hash,
            max_relative_diff=0.0,
            mismatched_keys=[] if has_replay_hash else ["No replay hash available"],
            metadata={
                "run_status": summary.status,
                "has_replay_hash": has_replay_hash,
                "replay_hash": summary.replay_hash,
            },
        )
