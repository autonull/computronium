"""TODO23 T23.1.8 — autopoiesis protocol surfaces exist and are checkable."""

from __future__ import annotations

import computronium.autopoiesis as ap
from computronium.autopoiesis import (
    Constitution,
    StagnationDetector,
)


class _Counting:
    def update(self, best_fitness: float) -> bool:
        return best_fitness < 0.5

    def admits(self, genome: dict[str, object]) -> bool:
        return "credit" in genome


def test_protocol_surface() -> None:
    assert set(ap.__all__) == {
        "Constitution",
        "FitnessMetric",
        "MutationOperator",
        "OperatorGenome",
        "SelectionPolicy",
        "StagnationDetector",
    }
    assert isinstance(_Counting(), StagnationDetector)
    assert isinstance(_Counting(), Constitution)
