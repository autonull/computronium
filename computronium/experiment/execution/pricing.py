"""What a declaration costs before it is spent (TODO48b R2).

A campaign's price used to be a session's guess: the run launched, and the
cells it had measured so far were the only evidence of how many it owed. That
makes fixture design trial-and-error — every "will this budget stop after six
records?" a paid probe.

The plan here is computed from the spec through the same builders the runner
walks, so it is evidence the space is the space the run will measure: the legal
cells are enumerated (no training), priced from the registry's measured seconds
per dynamics primitive, and summed. Three facts fall out that no single guess
gives: the price of the whole space, the cell a declared budget stops on, and
the primitives the declaration names that no legal cell can reach.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Final

from computronium.experiment.schema.harvest import AXIS_KIND_ORDER
from computronium.experiment.schema.registries import (
    FIXED_RUN_COST_SECONDS,
    MEASURED_CELL_SECONDS_REGIME,
    MEASURED_PARALLEL_SPEEDUP,
    cell_price_seconds,
)

# A sample size, not a price: a declaration that names every primitive is a
# factorial the walk cannot finish — the *illegal* candidates are the expensive
# majority, each one a compose that raises — and a dry run must stay a dry run.
# Past the bound the
# totals are the sample mean extrapolated over the declared count, and the plan
# says *that* rather than quoting a total it did not count.
# Increased from 24 to 5000 to handle full space where invalid combos dominate
# early iteration order (TODO49 Phase 2).
_PRICE_SCAN: Final = 5000
_PRICE_SAMPLE: Final = 24

if TYPE_CHECKING:
    from computronium.experiment.execution.search_space import (
        SearchSpace,
        ShapeResolver,
    )
    from computronium.experiment.schema.run_spec import RunSpec


@dataclass(frozen=True, slots=True)
class PricePlan:
    """A declaration's price, its stopping point, and what it cannot reach.

    Attributes:
        declared_cells: Cells the axes name, before legality (the factorial).
        truncated: Whether the walk hit the scan bound, making every count a
            lower bound.
        legal_cells: Cells the run can actually measure.
        per_dynamics_seconds: Projected seconds per dynamics primitive, by
            how many legal cells each carries.
        projected_seconds: Total projected seconds for every legal cell.
        cell_seconds: Each legal cell's projected seconds, in proposal order —
            the per-cell ledger the total and the stop index are derived from.
        budget_stop_cell: One-based index of the cell a declared budget cannot
            afford, or ``None`` when the space ends first.
        unreachable: Primitives the axes declare that no legal cell offers.
    """

    declared_cells: int
    legal_cells: int
    per_dynamics_seconds: dict[str, float]
    cell_seconds: tuple[float, ...]
    projected_seconds: float
    budget_stop_cell: int | None
    unreachable: tuple[tuple[str, str], ...]
    truncated: bool

    def render(self) -> str:
        """The plan as report lines: price, stop point, unreachable axes."""
        legal = f"{self.legal_cells}+" if self.truncated else str(self.legal_cells)
        lines = [
            f"declared cells: {self.declared_cells}  legal: {legal}"
            + (
                f" (priced from the first {self.legal_cells}; totals extrapolated)"
                if self.truncated
                else ""
            ),
            f"projected total: {self.projected_seconds:.1f}s "
            f"({self.projected_seconds / 60:.1f}m)",
            f"price regime: {MEASURED_CELL_SECONDS_REGIME}",
            f"per cell: n_seeds records at "
            f"{MEASURED_PARALLEL_SPEEDUP:.2f}x measured concurrency; "
            f"{FIXED_RUN_COST_SECONDS:.0f}s fixed run cost (not in the total)",
        ]
        if self.per_dynamics_seconds:
            priced = ", ".join(
                f"{name} {seconds:.1f}s"
                for name, seconds in sorted(
                    self.per_dynamics_seconds.items(), key=lambda kv: -kv[1]
                )
            )
            lines.append(f"per dynamics: {priced}")
        if self.budget_stop_cell is None:
            lines.append("budget: never binds — the space ends first")
        elif self.budget_stop_cell > self.legal_cells:
            lines.append(
                f"budget: affords all {self.legal_cells} legal cell(s); "
                f"the space ends first"
            )
        else:
            lines.append(
                f"budget: stops at cell {self.budget_stop_cell} of {self.legal_cells}"
            )
        if self.unreachable:
            named = ", ".join(f"{axis}={name}" for axis, name in self.unreachable)
            lines.append(f"declared but unreachable: {named}")
        return "\n".join(lines)


def price_plan(
    spec: RunSpec,
    space: SearchSpace,
    *,
    shape: ShapeResolver | None = None,
) -> PricePlan:
    """Price a declaration: enumerate its legal cells and sum their seconds.

    Args:
        spec: The run declaration to price.
        space: The space the declaration resolves to, carrying its tasks.
        shape: Task-shape resolver; ``task_shape`` when omitted.

    Returns:
        The declaration's price, where a declared budget stops it, and which
        declared primitives no legal cell offers.
    """
    from computronium.experiment.execution.evaluate import task_shape as default_shape
    from computronium.experiment.execution.search_space import (
        declared_cell_count,
        iter_candidates,
    )

    resolve = shape if shape is not None else default_shape

    # A cell is measured once per seed, and its seeds are measured
    # concurrently. The registry's price is a *serial* per-cell cost, so a
    # projection that omits either factor is wrong by it: §8.1 measured a 1.5x
    # understatement, and this session's own gate found 3.6x (233 s against a
    # 112 s bound) — the seeds multiply the work and the workers divide it, and
    # a plan that counts cells counts neither.
    per_record = max(1, spec.n_seeds) / MEASURED_PARALLEL_SPEEDUP

    per_dynamics: dict[str, float] = {}
    reached: dict[str, set[str]] = {axis.value: set() for axis in AXIS_KIND_ORDER}
    cells: list[float] = []
    legal = 0
    truncated = False
    cumulative = 0.0
    budget_stop: int | None = None

    for coordinate, _schedule in iter_candidates(
        spec, space, shape=resolve, max_scan=_PRICE_SCAN
    ):
        legal += 1
        if legal >= _PRICE_SAMPLE:
            truncated = True
            break
        seconds = (
            cell_price_seconds(coordinate.dynamics, epochs=spec.epochs) * per_record
        )
        cells.append(seconds)
        per_dynamics[coordinate.dynamics] = (
            per_dynamics.get(coordinate.dynamics, 0.0) + seconds
        )
        for axis in AXIS_KIND_ORDER:
            reached[axis.value].add(getattr(coordinate, axis.value))
        cumulative += seconds
        if (
            budget_stop is None
            and spec.budget_seconds is not None
            and cumulative > spec.budget_seconds
        ):
            budget_stop = legal

    declared = declared_cell_count(spec, space)
    if truncated:
        # The sample mean is the price of one legal cell; the declared count is
        # how many the factorial names. Both are printed, so the extrapolation
        # is checkable rather than merely claimed.
        cumulative = cumulative / legal * declared
        per_dynamics = {
            name: seconds / legal * declared for name, seconds in per_dynamics.items()
        }
    return PricePlan(
        declared_cells=declared,
        legal_cells=legal,
        per_dynamics_seconds=per_dynamics,
        cell_seconds=tuple(cells),
        projected_seconds=cumulative,
        budget_stop_cell=budget_stop,
        unreachable=() if truncated else _unreachable(space, reached),
        truncated=truncated,
    )


def _unreachable(
    space: SearchSpace, reached: dict[str, set[str]]
) -> tuple[tuple[str, str], ...]:
    """Declared primitives that no legal cell carries, axis by axis."""
    from computronium.experiment.schema.axis import StructuralAxis

    return tuple(
        (axis.value, name)
        for axis in StructuralAxis
        for name in space.primitives(axis)
        if name not in reached[axis.value]
    )


__all__ = ["PricePlan", "price_plan"]
