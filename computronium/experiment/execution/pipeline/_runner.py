"""The pipeline runner's public class, composed from its concern modules."""

from __future__ import annotations

from ._budget import _BudgetMixin
from ._checkpointing import _CheckpointMixin
from ._lifecycle import _LifecycleMixin
from ._stages import _StageMixin


class PipelineRunner(
    _LifecycleMixin,
    _StageMixin,
    _CheckpointMixin,
    _BudgetMixin,
):
    """S1-S11 pipeline runner with atomic append + reconciliation + wrapper obligations.

    Coordinates the full experiment lifecycle:
    - Stage progression (S1-S11) via Stage.run(ctx) -> Fragment dispatch
    - Round loop (S3-S10 repeat) with Decision-based termination
    - Budget management
    - Policy-driven candidate selection via SearchSpace
    - Backend execution with failure isolation (WP19)
    - Record persistence with reconciliation
    - Checkpointing and resume
    - Wrapper obligations: coverage, classification, traceability, failure isolation
    - EvidenceDrivenAllocator integration
    - Replay hash verification
    """
