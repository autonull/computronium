"""CellStream: unbounded, advancing, resumable generator of (Coordinate, Schedule).

The stream's one job is to hand the round loop fresh, legal, unmeasured cells
for as long as the deadline allows. It walks the structural grid one *page* at a
time (buffering every legal cell the page yields), skipping anything the store
has already measured or the admission gate has already rejected. A page that
yields nothing new means the declared structural grid is spent; the stream then
reports itself exhausted rather than raising, so a finite space ends the run in
bounded rounds instead of a crash and the astronomically large production space
never reaches that state at all.

The stream is the *only* producer of cells: re-proposing a measured cell is what
lets a run spin forever measuring nothing, so freshness is checked here, against
the store's own history, not deferred to a downstream screen.
"""

from __future__ import annotations

import logging
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from computronium.experiment.kernel.search_space import (
    SearchSpace,
    iter_candidates,
)

if TYPE_CHECKING:
    from computronium.experiment.execution.deadline import Deadline
    from computronium.experiment.execution.policy import Policy
    from computronium.experiment.kernel.evaluate import TaskShape
    from computronium.experiment.schema.coordinate import Coordinate, Schedule
    from computronium.experiment.schema.run_spec import RunSpec

logger = logging.getLogger(__name__)

# Candidates examined per page (a page size, never a cap).
_DEFAULT_PAGE_SIZE = 50_000

type ShapeResolver = Callable[[str], TaskShape]


@dataclass(slots=True)
class CellStreamState:
    """Persisted state for checkpoint/resume."""

    offset: int = 0
    page_size: int = _DEFAULT_PAGE_SIZE
    exhausted: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "offset": self.offset,
            "page_size": self.page_size,
            "exhausted": self.exhausted,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CellStreamState:
        return cls(
            offset=data.get("offset", 0),
            page_size=data.get("page_size", _DEFAULT_PAGE_SIZE),
            exhausted=data.get("exhausted", False),
        )


class CellStream:
    """Unbounded, advancing generator of (Coordinate, Schedule).

    Pages through the structural grid, buffering each page's legal cells and
    serving them by request size. A page with nothing new marks the stream
    exhausted; the pipeline reads that and ends the run rather than spinning.

    Args:
        spec: The run declaration.
        space: The run's active search space.
        shape: Task shape resolver for legality checks.
        deadline: Hard deadline for time enforcement.
        page_size: Candidates to examine per page (default 50k).
        is_measured: Predicate over a measurement key; ``True`` means the store
            already holds that cell and the stream must skip it.
    """

    def __init__(
        self,
        spec: RunSpec,
        space: SearchSpace,
        shape: ShapeResolver | None = None,
        deadline: Deadline | None = None,
        page_size: int = _DEFAULT_PAGE_SIZE,
        is_measured: Callable[[str], bool] | None = None,
    ) -> None:
        self._spec = spec
        self._space = space
        self._shape = shape
        self._deadline = deadline
        self._page_size = page_size
        self._is_measured = is_measured or (lambda _key: False)
        self._state = CellStreamState(page_size=page_size)
        self._rejected_keys: set[str] = set()
        self._exploit_policy: Policy | None = None
        self._iterator: Iterator[tuple[Coordinate, Schedule]] | None = None

    def set_exploit_policy(self, policy: Policy) -> None:
        """Set the exploit policy (reserved for the hyperparameter ladder)."""
        self._exploit_policy = policy

    def next(self, k: int) -> list[tuple[Coordinate, Schedule]]:
        """Get up to ``k`` fresh, legal, unmeasured cells.

        Returns fewer than ``k`` only when the deadline expires or the declared
        space is exhausted. Never raises for exhaustion: the pipeline reads
        :attr:`is_exhausted` and stops.

        The candidate page is pulled **lazily**: a cell is returned as soon as it
        is reached, not after the whole page is buffered. Buffering the page
        first meant the first cell waited on every legal candidate in a 50 000
        candidate page — and each legal candidate runs a composition dry-run —
        so a large space (the 3.3M-cell maturation grid) spent minutes before
        Cell 1 while consuming its own wall-clock budget.

        Args:
            k: Number of fresh cells to return.

        Returns:
            List of (Coordinate, Schedule) pairs, length <= k.
        """
        if self._deadline and self._deadline.soft_expired():
            logger.info("Deadline soft-expired, stream yielding empty")
            return []

        results: list[tuple[Coordinate, Schedule]] = []
        while len(results) < k and not self._state.exhausted:
            if self._iterator is None:
                self._open_page()
            iterator = self._iterator
            assert iterator is not None
            examined = False
            for coordinate, schedule in iterator:
                examined = True
                if self._deadline and self._deadline.soft_expired():
                    return results[:k]
                key = coordinate.measurement_key(schedule)
                if key in self._rejected_keys or self._is_measured(key):
                    continue
                results.append((coordinate, schedule))
                if len(results) >= k:
                    break
            else:
                # The page is spent; advance to the next one. The iterator lived
                # just long enough to serve this call, and is reopened at the
                # next page's offset so resume stays offset-indexed.
                self._iterator = None
                self._finish_page(examined)
                continue
            break
        return results[:k]

    def _open_page(self) -> None:
        """Open the candidate iterator at the current page offset."""
        self._iterator = iter_candidates(
            self._spec,
            self._space,
            deadline=self._deadline,
            shape=self._shape,
            check_composable=True,
            offset=self._state.offset,
            page_size=self._page_size,
        )

    def _finish_page(self, examined: bool) -> None:
        """Advance past a spent page, or mark the space exhausted when it was empty."""
        if not examined:
            self._state.exhausted = True
            logger.info(
                "Cell stream exhausted after offset=%d (no fresh cells in page)",
                self._state.offset,
            )
            return
        self._state.offset += self._page_size
        logger.debug("Cell stream advanced to offset=%d", self._state.offset)

    def add_rejected_key(self, key: str) -> None:
        """Add a key to the durable rejected set (admission gate)."""
        self._rejected_keys.add(key)

    def get_state(self) -> CellStreamState:
        """Get state for checkpoint/resume."""
        return self._state

    def set_state(self, state: CellStreamState) -> None:
        """Restore state for checkpoint/resume."""
        self._state = state
        self._iterator = None

    @property
    def is_exhausted(self) -> bool:
        """Whether the declared structural space has been fully walked."""
        return self._state.exhausted

    @property
    def offset(self) -> int:
        return self._state.offset


__all__ = ["CellStream", "CellStreamState"]
