"""One executed campaign: the declaration, the store, and its timing (R8).

Split from ``conftest.py`` so a lock may read the campaign's *numbers* without
reaching into the fixture module: the fixture hands this out, the locks only
read it. One name, one definition, four consumers.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from computronium.experiment.schema.record import Record
    from computronium.experiment.schema.run_spec import RunSpec


EXAMPLE = Path(__file__).resolve().parents[2] / "examples"
CAMPAIGN = EXAMPLE / "learning-rules-and-geometry-digits.yaml"


@dataclass(frozen=True, slots=True)
class Campaign:
    """One executed campaign: its declaration, its store, and its timing.

    ``elapsed_s`` is the fixture's own measurement of the run's walltime. It
    is *not* read from the store: D2's projection is a wall clock, and a store
    row that records the charged budget is a different quantity from the
    seconds the process actually spent. Both are carried, and the lock asserts
    the relationship between them rather than assuming one.
    """

    spec: RunSpec
    store_path: Path
    run_id: str
    status: str
    replay_hash: str
    budget_consumed_s: float
    elapsed_s: float
    records: tuple[Record, ...]

    def train_acc(self) -> list[float]:
        return [float(r.payload["train_acc"]) for r in self.records]  # type: ignore[attr-defined]

    def seconds_per_record(self) -> float:
        """D2's rate: measured walltime over measured records."""
        if not self.records:
            return 0.0
        return self.elapsed_s / len(self.records)
