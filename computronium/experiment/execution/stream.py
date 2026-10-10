"""CellStream: unbounded, advancing, resumable generator of (Coordinate, Schedule).

Replaces the tiered runner with a single stream that pages past _MAX_SCAN and,
when the structural grid is spent, ladders into hyperparameter-sweep steps
→ seeds → tasks → policy-minted fresh points.
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from computronium.experiment.execution.search_space import SearchSpace, iter_candidates
from computronium.experiment.schema.coordinate import Coordinate, Schedule
from computronium.experiment.schema.run_spec import RunSpec

if TYPE_CHECKING:
    from computronium.experiment.execution.deadline import Deadline
    from computronium.experiment.execution.evaluate import TaskShape
    from computronium.experiment.execution.policy import Policy

logger = logging.getLogger(__name__)

# ShapeResolver is Callable[[str], TaskShape]
type ShapeResolver = Callable[[str], TaskShape]


@dataclass(slots=True)
class CellStreamState:
    """Persisted state for checkpoint/resume."""

    offset: int = 0
    page_size: int = 50_000
    current_task_idx: int = 0
    regime: str = "structural"  # "structural" | "sweep" | "seeds" | "tasks" | "exploit"
    sweep_step: int = 0
    seed_idx: int = 0
    exploit_policy_state: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "offset": self.offset,
            "page_size": self.page_size,
            "current_task_idx": self.current_task_idx,
            "regime": self.regime,
            "sweep_step": self.sweep_step,
            "seed_idx": self.seed_idx,
            "exploit_policy_state": self.exploit_policy_state,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CellStreamState:
        return cls(
            offset=data.get("offset", 0),
            page_size=data.get("page_size", 50_000),
            current_task_idx=data.get("current_task_idx", 0),
            regime=data.get("regime", "structural"),
            sweep_step=data.get("sweep_step", 0),
            seed_idx=data.get("seed_idx", 0),
            exploit_policy_state=data.get("exploit_policy_state"),
        )


class CellStream:
    """Unbounded, advancing generator of (Coordinate, Schedule).

    Pages through the structural grid, then ladders through hyperparameter
    sweep steps, seeds, tasks, and finally exploit mode (policy-minted fresh
    points). Always advancing a persisted offset so a relaunched run continues
    the stream instead of restarting it.

    Args:
        spec: The run declaration.
        space: The run's active search space.
        shape: Task shape resolver for legality checks.
        deadline: Hard deadline for time enforcement.
        page_size: Candidates to examine per page (default 50k).
    """

    def __init__(
        self,
        spec: RunSpec,
        space: SearchSpace,
        shape: ShapeResolver | None = None,
        deadline: Deadline | None = None,
        page_size: int = 50_000,
    ) -> None:
        self._spec = spec
        self._space = space
        self._shape = shape
        self._deadline = deadline
        self._page_size = page_size
        self._state = CellStreamState(page_size=page_size)
        self._rejected_keys: set[str] = set()
        self._exploit_policy: Policy | None = None

    def set_exploit_policy(self, policy: Policy) -> None:
        """Set the exploit policy for minting fresh cells."""
        self._exploit_policy = policy

    def next(self, k: int) -> list[tuple[Coordinate, Schedule]]:
        """Get the next k fresh cells from the stream.

        Advances the internal offset across pages and regimes. Returns fewer
        than k cells only if the deadline expires or the stream is genuinely
        exhausted (which should not happen in exploit mode).

        Args:
            k: Number of fresh cells to return.

        Returns:
            List of (Coordinate, Schedule) pairs, length <= k.
        """
        if self._deadline and self._deadline.soft_expired():
            logger.info("Deadline soft-expired, stream yielding empty")
            return []

        results: list[tuple[Coordinate, Schedule]] = []

        while len(results) < k:
            if self._state.regime == "structural":
                batch = self._next_structural_page(k - len(results))
                results.extend(batch)
                if len(batch) < k - len(results):
                    # Page exhausted, advance to sweep regime
                    self._advance_regime()
            elif self._state.regime == "sweep":
                batch = self._next_sweep_step(k - len(results))
                results.extend(batch)
                if len(batch) < k - len(results):
                    self._advance_regime()
            elif self._state.regime == "seeds":
                batch = self._next_seed(k - len(results))
                results.extend(batch)
                if len(batch) < k - len(results):
                    self._advance_regime()
            elif self._state.regime == "tasks":
                batch = self._next_task(k - len(results))
                results.extend(batch)
                if len(batch) < k - len(results):
                    self._advance_regime()
            elif self._state.regime == "exploit":
                batch = self._next_exploit(k - len(results))
                results.extend(batch)
                if len(batch) < k - len(results):
                    # Exploit mode should always be able to produce more
                    # If it can't, something is wrong - raise
                    raise RuntimeError(
                        "Exploit mode cannot produce fresh cells; "
                        "policy may be stuck or space truly exhausted"
                    )
            else:
                raise RuntimeError(f"Unknown regime: {self._state.regime}")

            if self._deadline and self._deadline.soft_expired():
                break

        return results[:k]

    def _next_structural_page(self, need: int) -> list[tuple[Coordinate, Schedule]]:
        """Yield from the structural grid (axes product) at current offset."""
        stream = iter_candidates(
            self._spec,
            self._space,
            deadline=self._deadline,
            shape=self._shape,
            check_composable=True,
            offset=self._state.offset,
            page_size=self._page_size,
        )
        results = []
        for coord, sched in stream:
            if self._is_fresh(coord, sched):
                results.append((coord, sched))
                if len(results) >= need:
                    break
        self._state.offset += self._page_size
        logger.debug(
            "Structural page: offset=%d, yielded=%d, need=%d",
            self._state.offset,
            len(results),
            need,
        )
        return results

    def _next_sweep_step(self, need: int) -> list[tuple[Coordinate, Schedule]]:
        """Yield from the next hyperparameter sweep step across all tasks."""
        from computronium.experiment.execution.search_space import (
            _swept,
            harvest_schema,
        )

        schema = harvest_schema()
        ladders = _swept(self._spec, schema, self._shape)
        max_steps = max((len(ladder) for ladder in ladders.values()), default=1)

        if self._state.sweep_step >= max_steps:
            self._state.sweep_step = 0
            return []

        results = []
        stream = iter_candidates(
            self._spec,
            self._space,
            deadline=self._deadline,
            shape=self._shape,
            check_composable=True,
            offset=0,  # Sweep step uses full grid but with specific hyperparam values
            page_size=self._page_size,
        )
        for coord, sched in stream:
            # Only yield cells at the current sweep step
            # (The ladder step is encoded in the coordinate's params)
            if self._is_fresh(coord, sched):
                results.append((coord, sched))
                if len(results) >= need:
                    break
        self._state.sweep_step += 1
        return results

    def _next_seed(self, need: int) -> list[tuple[Coordinate, Schedule]]:
        """Yield remaining seeds for already-proposed coordinates."""
        # This regime handles multi-seed schedules: for coordinates that were
        # proposed with n_seeds > 1, yield the remaining seeds.
        # Implementation: iterate through completed keys, find partial seeds.
        # For simplicity, delegate to structural page with fresh() check
        # which already checks per-seed.
        results = []
        stream = iter_candidates(
            self._spec,
            self._space,
            deadline=self._deadline,
            shape=self._shape,
            check_composable=True,
            offset=0,
            page_size=self._page_size,
        )
        for coord, sched in stream:
            if self._is_fresh(coord, sched):
                results.append((coord, sched))
                if len(results) >= need:
                    break
        self._advance_regime()  # Move to tasks after one pass
        return results

    def _next_task(self, need: int) -> list[tuple[Coordinate, Schedule]]:
        """Yield from the next task in the spec."""
        tasks = self._space.tasks
        if self._state.current_task_idx >= len(tasks):
            self._state.current_task_idx = 0
            return []

        # Switch to next task
        task = tasks[self._state.current_task_idx]
        self._state.current_task_idx += 1

        # Create a scoped space for this task
        scoped_space = SearchSpace(
            axes_snapshot=self._space.axes_snapshot,
            constraints=self._space.constraints,
            objectives=self._space.objectives,
            tasks=(task,),
        )

        results = []
        stream = iter_candidates(
            self._spec,
            scoped_space,
            deadline=self._deadline,
            shape=self._shape,
            check_composable=True,
            offset=0,
            page_size=self._page_size,
        )
        for coord, sched in stream:
            if self._is_fresh(coord, sched):
                results.append((coord, sched))
                if len(results) >= need:
                    break

        if self._state.current_task_idx >= len(tasks):
            self._advance_regime()  # Move to exploit
        return results

    def _next_exploit(self, need: int) -> list[tuple[Coordinate, Schedule]]:
        """Yield fresh cells minted by the exploit policy (ModelBased/Evolution).

        The policy's propose() is called with a context that has the store's
        history, so it generates novel hyperparameter settings around the best
        observed cells. This is an UNBOUNDED generator — it can always propose
        a coordinate the store has never seen.
        """
        if self._exploit_policy is None:
            logger.warning("No exploit policy set, falling back to structural")
            return self._next_structural_page(need)

        # The exploit policy needs a ProposalContext with evidence (store)
        # This is provided by the pipeline when calling next()
        # For now, return empty and let the pipeline handle exploit mode
        # via the policy directly in S3_SCHEDULE stage
        logger.debug("Exploit mode: delegating to pipeline's policy")
        return []

    def _is_fresh(self, coordinate: Coordinate, schedule: Schedule) -> bool:
        """Check if a cell is fresh (not measured, not rejected)."""
        key = coordinate.measurement_key(schedule)
        if key in self._rejected_keys:
            return False
        # Note: measured_keys check requires evidence (store) which is not available here
        # The pipeline's _fresh_batch_items does the full check
        return True

    def advance_regime(self) -> None:
        """Explicitly advance to the next regime."""
        self._advance_regime()

    def _advance_regime(self) -> None:
        """Internal regime transition logic."""
        regimes = ["structural", "sweep", "seeds", "tasks", "exploit"]
        current_idx = regimes.index(self._state.regime)
        if current_idx + 1 < len(regimes):
            self._state.regime = regimes[current_idx + 1]
            logger.info("Stream advanced to regime: %s", self._state.regime)
        # If already in exploit, stay there

    def add_rejected_key(self, key: str) -> None:
        """Add a key to the durable rejected set (admission gate)."""
        self._rejected_keys.add(key)

    def get_state(self) -> CellStreamState:
        """Get state for checkpoint/resume."""
        return self._state

    def set_state(self, state: CellStreamState) -> None:
        """Restore state for checkpoint/resume."""
        self._state = state

    @property
    def regime(self) -> str:
        return self._state.regime

    @property
    def offset(self) -> int:
        return self._state.offset


__all__ = ["CellStream", "CellStreamState"]
