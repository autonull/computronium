"""Joint State Architecture: re-exports the canonical state classes.

CompositeState / StateVariable / StateRegistry are single-sourced in
``computronium.state``; this module adds the trajectory recorder on top
of them.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from torch import Tensor

from computronium.state import CompositeState, StateRegistry, StateVariable

if TYPE_CHECKING:
    from computronium.core.joint.trajectory import JointTrajectory

__all__ = [
    "CompositeState",
    "JointTrajectoryRecorder",
    "StateRegistry",
    "StateVariable",
]


@dataclass(slots=True)
class JointTrajectoryRecorder:
    """Records joint trajectories with gradient checkpointing support.

    Addresses autograd graph fragmentation from long settling trajectories
    by recording only what's needed for credit assignment, with optional
    checkpointing for memory efficiency.

    Attributes:
        max_steps: Maximum trajectory length to record.
        checkpoint_interval: Steps between gradient checkpoints (0 = no checkpointing).
        record_plastic: Whether to record ψ trajectory.
        record_substrate: Whether to record σ trajectory.
    """

    max_steps: int = 1000
    checkpoint_interval: int = 0
    record_plastic: bool = True
    record_substrate: bool = True

    # Internal trajectory buffers
    _activity_traj: list[dict[str, Tensor]] = field(default_factory=list, init=False)
    _plastic_traj: list[dict[str, Tensor]] = field(default_factory=list, init=False)
    _substrate_traj: list[dict[str, Tensor]] = field(default_factory=list, init=False)
    _checkpoint_indices: list[int] = field(default_factory=list, init=False)

    def record(self, z: CompositeState) -> None:
        """Record a joint state snapshot.

        Non-tensor activity entries (loss scalars, metrics dicts) are
        skipped — the trajectory records the x/ψ/σ tensor state only.

        Args:
            z: Current joint state to record.
        """
        if len(self._activity_traj) >= self.max_steps:
            return

        # Clone activity (always needed for credit assignment)
        self._activity_traj.append({
            k: v.detach().clone()
            for k, v in z.activity.items()
            if isinstance(v, Tensor)
        })

        # Optionally record plastic state
        if self.record_plastic:
            self._plastic_traj.append({
                k: v.detach().clone() for k, v in z.plastic.items()
            })

        # Optionally record substrate state
        if self.record_substrate:
            self._substrate_traj.append({
                k: v.detach().clone() for k, v in z.substrate.items()
            })

        # Mark checkpoint if interval set
        if (
            self.checkpoint_interval > 0
            and len(self._activity_traj) % self.checkpoint_interval == 0
        ):
            self._checkpoint_indices.append(len(self._activity_traj) - 1)

    def get_trajectory(self) -> JointTrajectory:
        """Return recorded trajectory as an immutable JointTrajectory."""
        # Import locally to avoid circular dependency
        import computronium.core.joint.trajectory as trajectory_module

        return trajectory_module.JointTrajectory(
            activity=self._activity_traj,
            plastic=self._plastic_traj if self.record_plastic else [],
            substrate=self._substrate_traj if self.record_substrate else [],
            checkpoint_indices=self._checkpoint_indices,
        )

    def clear(self) -> None:
        """Clear recorded trajectory."""
        self._activity_traj.clear()
        self._plastic_traj.clear()
        self._substrate_traj.clear()
        self._checkpoint_indices.clear()

    def __len__(self) -> int:
        return len(self._activity_traj)
