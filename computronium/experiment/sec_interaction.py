"""S3: the interaction slice — which axes change each other (TODO95 P3).

The census measured one axis at a time at the fixed base. It cannot say whether
one axis's effect survives another axis's level. The pair is read from the map:
the two axes with the most variance over ``binding=bound`` rows. A row that ran
in a swapped box, that refused, or that never trained is not a comparable cell
and does not rank (TODO95 D3/D8).

The slice is seated at the base box, varies only the pair, and reads the
interaction as a difference-in-differences: the effect of the second axis at
the first axis's baseline minus the effect at its own. The base level of the
pair is the box's base; when that level is inert in its axis it is the
factorial's baseline, not a result about the axis (TODO95 D8).

A screen emits the number; it never ranks. The effect carries an interval from
the confirmed seeds, a slice whose control sits inside the bar is ``no_power``
before it is priced, and one seed per cell carries no interval at all
(TODO95 S2/S3).
"""

from __future__ import annotations

import math
import statistics
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Final

from computronium.acceleration.spec import axis_segment

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping

__all__ = [
    "INTERACTION_SEEDS",
    "AxisSpread",
    "InteractionCell",
    "InteractionEffect",
    "SlicePlan",
    "analysis",
    "axis_spreads",
    "bound_rows",
    "interaction_effect",
    "plan_slice",
]

#: The seeds per cell in the confirm stage. One seed screens a cell; three
#: seeds carry the pair's interval (TODO95 S3). A claim needs five paired
#: seeds at matched boxes, so this slice reports an interval, never a verdict.
INTERACTION_SEEDS: Final[int] = 3

#: The two-sided interval of the confirm stage. A screen reports the effect's
#: uncertainty instead of a ranking.
CONFIDENCE: Final[float] = 0.95


def _level(row: Mapping[str, Any]) -> str:
    """The varied axis value a map row names, from its primitive ID."""
    return str(row.get("primitive", "")).rsplit(".", 1)[-1]


def _val_acc(row: Mapping[str, Any]) -> float | None:
    measurement = row.get("measurement") or {}
    value = measurement.get("val_acc")
    return None if value is None else float(value)


def bound_rows(map_data: Mapping[str, Any]) -> list[dict[str, Any]]:
    """The measured, bound rows that rank the axes (TODO95 P3).

    A row is comparable only in the box it ran at: a swapped row carries
    another difference than its varied axis, so it does not rank. A defect is
    an execution fact and never carries an axis's variance.
    """
    rows: list[dict[str, Any]] = []
    for row in (map_data.get("primitives") or {}).values():
        if row.get("status") != "measured" or row.get("binding") != "bound":
            continue
        if row.get("swapped") or _val_acc(row) is None:
            continue
        rows.append(row)
    return rows


def _base_row(
    map_data: Mapping[str, Any], axis: str, value: str | None
) -> dict[str, Any] | None:
    """The axis's base-level row, bound or inert, measured in the box."""
    if value is None:
        return None
    for row in (map_data.get("primitives") or {}).values():
        if (
            axis_segment(str(row.get("axis", ""))) == axis
            and _level(row) == value
            and row.get("status") == "measured"
            and _val_acc(row) is not None
        ):
            return row
    return None


@dataclass(frozen=True, slots=True)
class AxisSpread:
    """One axis's variance over its bound rows and its candidate levels."""

    axis: str
    variance: float
    count: int
    base: str
    base_val_acc: float
    base_binding: str | None
    #: The bound values, the largest deviation from the base level first.
    arms: tuple[tuple[str, float], ...]

    @property
    def binds_at_base(self) -> bool:
        """Whether the axis acts at its base level in this box."""
        return self.base_binding == "bound"


def axis_spreads(map_data: Mapping[str, Any]) -> list[AxisSpread]:
    """Every factor-ready axis, ranked by variance over its bound rows.

    An axis is factor-ready when the box has a measured base level and at least
    one bound row: without the baseline there is no factorial, and without a
    bound row the axis never acted in this box (TODO95 D8).
    """
    rows = bound_rows(map_data)
    base = map_data.get("base") or {}
    by_axis: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        by_axis.setdefault(axis_segment(str(row.get("axis", ""))), []).append(row)

    spreads: list[AxisSpread] = []
    for axis, axis_rows in by_axis.items():
        base_level = base.get(axis)
        base_row = _base_row(map_data, axis, base_level)
        if base_level is None or base_row is None:
            continue
        base_acc = _val_acc(base_row)
        if base_acc is None:
            continue
        anchor: float = base_acc
        measured: list[tuple[str, float]] = []
        for row in axis_rows:
            value = _val_acc(row)
            level = _level(row)
            if value is not None and level != base_level:
                measured.append((level, value))
        if not measured:
            continue
        measured.sort(key=lambda arm: (-abs(arm[1] - anchor), arm[0]))
        values = [value for row in axis_rows if (value := _val_acc(row)) is not None]
        spreads.append(
            AxisSpread(
                axis=axis,
                variance=statistics.pvariance(values),
                count=len(axis_rows),
                base=str(base_level),
                base_val_acc=anchor,
                base_binding=base_row.get("binding"),
                arms=tuple(measured),
            )
        )
    return sorted(spreads, key=lambda spread: (-spread.variance, spread.axis))


def _seat(
    first: AxisSpread,
    second: AxisSpread,
    allowed: Callable[[dict[str, str]], bool],
) -> dict[str, tuple[str, str]] | None:
    """The largest legal 2×2: the joint displacement picks the arms.

    An arm that composes with its own base but not with the other axis's base
    has no cell at this box, so it is not a factor level here. The system's
    validator decides; a pair with no legal 2×2 is refused, not swapped.
    """
    candidate: list[tuple[float, str, str]] = []
    for level_a, acc_a in first.arms:
        for level_b, acc_b in second.arms:
            displacement = abs(acc_a - first.base_val_acc) + abs(
                acc_b - second.base_val_acc
            )
            candidate.append((displacement, level_a, level_b))
    candidate.sort(key=lambda arm: (-arm[0], arm[1], arm[2]))
    for _displacement, level_a, level_b in candidate:
        cells = [
            {first.axis: a, second.axis: b}
            for a in (first.base, level_a)
            for b in (second.base, level_b)
        ]
        if all(allowed(levels) for levels in cells):
            return {
                first.axis: (first.base, level_a),
                second.axis: (second.base, level_b),
            }
    return None


@dataclass(frozen=True, slots=True)
class SlicePlan:
    """The factorial the map allocates: a pair and its two levels."""

    spreads: tuple[AxisSpread, ...]
    levels: dict[str, tuple[str, str]]

    @property
    def pair(self) -> tuple[AxisSpread, AxisSpread]:
        """The two axes with the most variance, in rank order."""
        return self.spreads[0], self.spreads[1]

    @property
    def axes(self) -> tuple[str, str]:
        return self.pair[0].axis, self.pair[1].axis

    def combinations(self) -> list[dict[str, str]]:
        """The 2×2 levels, base cell first, then one-axis swaps."""
        first, second = self.pair
        base_a, varied_a = self.levels[first.axis]
        base_b, varied_b = self.levels[second.axis]
        return [
            {first.axis: base_a, second.axis: base_b},
            {first.axis: varied_a, second.axis: base_b},
            {first.axis: base_a, second.axis: varied_b},
            {first.axis: varied_a, second.axis: varied_b},
        ]


def plan_slice(
    map_data: Mapping[str, Any],
    *,
    legal: Callable[[dict[str, str]], bool] | None = None,
) -> SlicePlan | None:
    """The interaction slice the map allocates, or ``None`` when it cannot.

    Two factor-ready axes are the minimum: one axis at a time has no
    interaction, and a pair without a base level has no baseline. The pair is
    the top two by variance; its arms are the largest 2×2 the system's
    validator accepts, or the slice is refused with those axes unchanged.
    """
    spreads = axis_spreads(map_data)
    if len(spreads) < 2:
        return None
    first, second = spreads[0], spreads[1]
    levels = _seat(first, second, legal or (lambda _levels: True))
    if levels is None:
        return None
    return SlicePlan(spreads=tuple(spreads), levels=levels)


@dataclass(frozen=True, slots=True)
class InteractionCell:
    """One run of the factorial: its two levels, box, seed and replay hash."""

    levels: dict[str, str]
    seed: int
    status: str  # measured | defect | refused
    val_acc: float | None
    loss: float | None
    walltime_s: float | None
    replay_hash: str | None
    box: dict[str, Any]
    reason: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "levels": dict(self.levels),
            "seed": self.seed,
            "status": self.status,
            "val_acc": self.val_acc,
            "loss": self.loss,
            "walltime_s": self.walltime_s,
            "replay_hash": self.replay_hash,
            "box": self.box,
            "reason": self.reason,
        }


@dataclass(frozen=True, slots=True)
class InteractionEffect:
    """The difference-in-differences and its interval, never a ranking."""

    effect: float
    lower: float | None
    upper: float | None
    seeds: int
    spans_zero: bool | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "effect": self.effect,
            "lower": self.lower,
            "upper": self.upper,
            "seeds": self.seeds,
            "spans_zero": self.spans_zero,
        }


def _t_quantile(degrees_of_freedom: int) -> float:
    from scipy.stats import t

    return float(t.ppf(0.5 + CONFIDENCE / 2, degrees_of_freedom))


def interaction_effect(
    plan: SlicePlan,
    cells: list[InteractionCell],
) -> InteractionEffect | None:
    """The 2×2 residual (effect at the second level minus effect at the base).

    The interval pools the four cells' seed variance. A cell with one seed has
    no variance, so the effect is reported without bounds (TODO95 S3).

    Args:
        plan: The factorial the cells belong to.
        cells: The runs, each keyed by its two levels and its seed.

    Returns:
        The effect, or ``None`` when a cell of the 2×2 did not measure.
    """
    first, second = plan.pair
    quad: dict[tuple[str | None, str | None], list[InteractionCell]] = {}
    for cell in cells:
        key = (cell.levels.get(first.axis), cell.levels.get(second.axis))
        quad.setdefault(key, []).append(cell)
    base_a, varied_a = plan.levels[first.axis]
    base_b, varied_b = plan.levels[second.axis]
    wanted = [
        (base_a, base_b),
        (varied_a, base_b),
        (base_a, varied_b),
        (varied_a, varied_b),
    ]
    runs = [quad.get(key, []) for key in wanted]
    if any(
        not group or any(cell.status != "measured" for cell in group) for group in runs
    ):
        return None
    values = [
        [cell.val_acc for cell in group if cell.val_acc is not None] for group in runs
    ]
    if any(
        len(group_values) != len(group) for group_values, group in zip(values, runs)
    ):
        return None
    means = [statistics.fmean(group_values) for group_values in values]
    effect = means[3] - means[1] - means[2] + means[0]
    seeds = min(len(group_values) for group_values in values)
    if seeds < 2:
        return InteractionEffect(effect, None, None, seeds, None)
    variance = sum(
        statistics.pvariance(group_values) / len(group_values)
        for group_values in values
    )
    degrees = sum(len(group_values) - 1 for group_values in values)
    half = _t_quantile(degrees) * math.sqrt(variance)
    return InteractionEffect(
        effect=effect,
        lower=effect - half,
        upper=effect + half,
        seeds=seeds,
        spans_zero=effect - half <= 0.0 <= effect + half,
    )


def analysis(plan: SlicePlan) -> dict[str, Any]:
    """The layer's design half: the ranked axes and the pair's levels."""
    return {
        "pair": list(plan.axes),
        "variance": {
            spread.axis: {
                "variance": spread.variance,
                "rows": spread.count,
                "base": spread.base,
                "binds_at_base": spread.binds_at_base,
            }
            for spread in plan.spreads
        },
        "levels": {axis: list(levels) for axis, levels in plan.levels.items()},
    }
