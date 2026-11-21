"""TODO98 P1's instrument: the tiny fit, its control, and the declared knob.

A law is tested by one deterministic fit on the family's declared shape:
16 samples, at most 200 optimizer steps, at three learning rates. The fit
must reach a tenth of its untrained loss under some legal setting (L-b), the
same fit must fail with the law's mechanism removed (L-b⁻), and the knob the
law declares must move the fit (L-c). A fit that passes with the mechanism
removed measures the optimizer: that is a test defect, never a result.

The cell is the one the screen prices: the family's base box, with the law's
own axis, at the family's declared input shape and parameter budget. The
batch is that shape's first ``SAMPLES`` rows, seeded, so no dataset and no
shuffle enters the mechanism's verdict.

This module decides nothing about which law runs: the batch driver
(``scripts/probes/p1_law_surface.py``) owns the waves and the calibration.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, replace
from typing import TYPE_CHECKING, Any, Final

import torch

from computronium.primitives import cases

if TYPE_CHECKING:
    from computronium.experiment.kernel.compose import ComposedCell
    from computronium.experiment.schema.coordinate import Coordinate
    from computronium.primitives.registry import PrimitiveSpec

__all__ = [
    "FLAT",
    "GRID",
    "REACHED",
    "SAMPLES",
    "STEPS",
    "Fit",
    "FitError",
    "Problem",
    "cell",
    "control",
    "coordinate",
    "decide",
    "family",
    "knob",
    "measure",
    "problem",
    "values",
]

#: The declared fit: samples per batch, the step ceiling, the reach factor
#: of the untrained loss, and the learning-rate factors a legal setting may
#: take. A grid point outside a declared bound is dropped by the caller.
SAMPLES: Final[int] = 16
STEPS: Final[int] = 200
REACHED: Final[float] = 0.1
#: What a passing control says: the fit measures the optimizer, not the law.
CONTROL_REACHES: Final[str] = "the control reaches: the fit measures the optimizer"
GRID: Final[tuple[float, ...]] = (1.0, 10.0, 0.1)
#: Steps of an unchanged loss that decide a frozen fit: a mechanism that
#: contributes nothing leaves the loss identical, and no later step moves it.
FLAT: Final[int] = 20


#: The knob each axis reads, in preference order. The first one the law
#: declares is L-c's knob; an axis none of whose knobs the law declares has
#: no L-c, and the row says so instead of tuning something else.
class FitError(RuntimeError):
    """The fit could not run: the cell refuses its batch, or the step raises."""


@dataclass(frozen=True, slots=True)
class Fit:
    """One tiny fit: its untrained loss, its last loss, and what it spent."""

    loss: float
    final: float
    steps: int
    seconds: float
    killed: bool = False

    @property
    def reached(self) -> bool:
        """The fit reached a tenth of its untrained loss."""
        return not self.killed and self.final <= REACHED * self.loss

    @property
    def moved(self) -> bool:
        """The loss is finite and not constant: an error-blind law's contract."""
        return not self.killed and self.final != self.loss

    @property
    def signature(self) -> tuple[float, int]:
        """What a knob must move: the last loss and the steps it took."""
        return (round(self.final, 6), self.steps)


@dataclass(frozen=True, slots=True)
class Problem:
    """The deterministic batch a fit runs on."""

    x: torch.Tensor
    y: torch.Tensor
    kwargs: dict[str, Any]


def family(spec: PrimitiveSpec) -> str:
    """The cheapest declared family that owns the law's base box."""
    from computronium.primitives.surface import _family

    return _family(spec)


def _declared(spec: PrimitiveSpec) -> tuple[tuple[int, ...], int]:
    """The family's declared input shape and output dim, from the registry."""
    from computronium.experiment.registry.task_registry import TaskRegistry
    from computronium.experiment.sec_pilot import BASE_BOXES

    box = BASE_BOXES[family(spec)]
    enriched = TaskRegistry().get(box.task_id)
    shape = tuple(enriched.input_shape or (cases.MICRO_INPUT_SHAPE))
    return shape, int(enriched.output_dim or cases.MICRO_OUTPUT_DIM)


def coordinate(spec: PrimitiveSpec, lr: float | None = None) -> Coordinate:
    """The family's base box with the law's own axis, at an optional lr.

    Args:
        spec: The law to compose.
        lr: The learning rate to override; ``None`` keeps the base box's.

    Returns:
        The coordinate the cell composes at.
    """
    from computronium.experiment.sec_loop import _base_axes, _coordinate
    from computronium.experiment.sec_pilot import BASE_BOXES

    box = BASE_BOXES[family(spec)]
    axes = _base_axes(box.task_id)
    axes[spec.axis] = spec.id.rsplit(".", 1)[-1]
    declared = _coordinate(axes)
    if lr is None:
        return declared
    return replace(declared, params={**declared.params, "update.step_size": lr})


def _compose(
    declared: Coordinate,
    shape: tuple[int, ...],
    output_dim: int,
    param_budget: int,
) -> ComposedCell:
    """Compose one cell at ``declared``, with the family's declared shape."""
    from computronium.experiment.kernel.compose import compose_cell_system

    return compose_cell_system(
        coordinate=declared,
        geometry={},
        input_shape=shape,
        output_dim=output_dim,
        param_budget=param_budget,
    )


def cell(spec: PrimitiveSpec, declared: Coordinate, seed: int = 0) -> ComposedCell:
    """Compose the law's cell at ``declared``, with the family's own shape.

    The composition is seeded, so two fits of one declaration start from the
    same weights: an unseeded cell turns the noise into an apparent response.
    """
    from computronium.experiment.sec_pilot import BASE_BOXES

    torch.manual_seed(seed)
    shape, output_dim = _declared(spec)
    return _compose(declared, shape, output_dim, BASE_BOXES[family(spec)].param_budget)


def _input(geometry: Any, seed: int, label_dim: int = 0) -> torch.Tensor:
    """The fit's batch for a geometry's declared topology.

    A label-channel credit's geometry is composed over the augmented width
    (the target's own features are appended by the channel seam), so the
    batch carries the plain width and the seam appends the labels.
    """
    shape = cases._input_shape(geometry)
    if label_dim and geometry.topology_type not in {"graph", "causal_transformer"}:
        shape = (*shape[:-1], shape[-1] - label_dim)
    generator = torch.Generator().manual_seed(seed)
    if geometry.topology_type == "graph":
        return torch.randn(shape, generator=generator)
    shape = (SAMPLES, *shape[1:])
    if geometry.topology_type == "causal_transformer":
        return torch.randint(0, geometry.input_dim, shape, generator=generator)
    return torch.randn(shape, generator=generator)


def problem(system: Any, composed: ComposedCell, seed: int = 0) -> Problem:
    """The seeded batch, with targets read from the logits' own index shape."""
    label_dim = (
        composed.config.credit.label_dim if composed.config.credit.label_channel else 0
    )
    x = _input(composed.config.geometry, seed, label_dim)
    with torch.no_grad():
        logits = system.forward(x)
    generator = torch.Generator().manual_seed(seed + 1)
    y = torch.randint(
        0, logits.shape[-1], tuple(logits.shape[:-1]), generator=generator
    )
    return Problem(x=x, y=y, kwargs={})


def measure(
    system: Any,
    batch: Problem,
    *,
    steps: int = STEPS,
    seconds: float | None = None,
    criterion: str = "reach",
) -> Fit:
    """Run the fit, stopping when decided, killed past ``seconds``.

    A fit stops when it reaches its criterion, when the mechanism leaves the
    loss identical for ``FLAT`` steps (a frozen mechanism is decided, not
    slow), or when its watchdog expires. A killed fit has no verdict: the
    caller refuses the cell rather than reading it as a failure.

    Args:
        criterion: ``"reach"`` for a tenth of the untrained loss;
            ``"moved"`` for an error-blind law, whose contract is a finite,
            non-constant loss rather than a floor.
    """
    started = time.monotonic()
    losses: list[float] = []
    for step in range(steps):
        try:
            metrics = system.train_step(batch.x, batch.y, **batch.kwargs)
        except Exception as exc:
            msg = f"step {step}: {type(exc).__name__}: {exc}"
            raise FitError(msg) from exc
        losses.append(float(metrics["loss"]))
        if not torch.isfinite(torch.tensor(losses[-1])):
            break
        if criterion == "moved" and losses[-1] != losses[0]:
            break
        if criterion == "reach" and losses[-1] <= REACHED * losses[0]:
            break
        if len(losses) > FLAT and len(set(losses[-FLAT:])) == 1:
            break
        if seconds is not None and time.monotonic() - started > seconds:
            return Fit(
                losses[0], losses[-1], len(losses), time.monotonic() - started, True
            )
    return Fit(losses[0], losses[-1], len(losses), time.monotonic() - started)


class _ZeroGradient:
    """A credit whose pseudo-gradient is zero: the mechanism's signal removed."""

    def __init__(self, credit: Any) -> None:
        self._credit = credit

    def __getattr__(self, name: str) -> Any:
        return getattr(self._credit, name)

    def compute_pseudo_gradient(
        self, states: Any, loss: Any, geometry: Any
    ) -> list[Any]:
        """The law's gradients, zeroed: the fit sees no credit signal."""
        grads = self._credit.compute_pseudo_gradient(states, loss, geometry)
        return [torch.zeros_like(grad) for grad in grads]


class _FrozenUpdate:
    """A parameter update that moves nothing: the mechanism's step removed."""

    def __init__(self, update: Any) -> None:
        self._update = update

    def __getattr__(self, name: str) -> Any:
        return getattr(self._update, name)

    def step(
        self,
        params: dict[str, Any],
        pseudo_grads: list[Any],
        geometry: Any,
        bias_grads: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """The parameters, unchanged."""
        return dict(params)


def control(spec: PrimitiveSpec, declared: Coordinate, seed: int = 0) -> ComposedCell:
    """The same cell with the law's mechanism removed.

    A credit's pseudo-gradient is zeroed and an update's step is identity:
    those are the axis's own contribution, so removing it keeps the cell and
    cuts the signal. A geometry, a settle, a substrate and a plasticity law
    are replaced by their declared neutral companion — feedforward,
    instantaneous, digital, null — because each of those laws is a mechanism
    *over* its companion, and the companion is the removal the repository
    already declares.

    The replacement is a recipe, not a parameter patch: the pipeline rebuilds
    a geometry's weights each step, so zeroing them in place is undone at the
    first step (measured: a zeroed nca cell trained to the same loss).
    """
    from dataclasses import replace

    # A companion is another law: the varied axis's own overrides would be
    # dead configuration on it, and `compose_configs` refuses them by name.
    def companion(**axes: str) -> ComposedCell:
        params = {
            key: value
            for key, value in declared.params.items()
            if not key.startswith(f"{spec.axis}.")
        }
        return cell(spec, replace(declared, params=params, **axes), seed)

    match spec.axis:
        case "geometry":
            return companion(geometry="feedforward")
        case "dynamics":
            return companion(dynamics="instantaneous")
        case "substrate":
            return companion(substrate="digital")
        case "plasticity":
            return companion(plasticity="null")
        case "credit":
            composed = cell(spec, declared, seed)
            composed.system.credit = _ZeroGradient(composed.system.credit)
            return composed
        case "update":
            composed = cell(spec, declared, seed)
            composed.system.update = _FrozenUpdate(composed.system.update)
            return composed
        case other:
            msg = f"no control for axis {other!r}"
            raise ValueError(msg)


def knob(
    spec: PrimitiveSpec, declared: Coordinate
) -> tuple[str, Any, dict[str, Any]] | None:
    """The first active numeric knob of the law's axis, with its params.

    The composed cell is the authority: it records the values the harvest
    actually applied (``axis.name``), so a declared-but-inactive knob — the
    one its availability predicate switches off at this box — is never L-c's
    knob, and the override that varies it is never refused as dead config.
    The order is the axis's own (sorted names), so no preference list is
    kept here.

    Returns:
        The knob's name, its composed value, and the params that set it; or
        ``None`` when the cell records no numeric knob on the axis.
    """
    applied = cell(spec, declared).params
    prefix = f"{spec.axis}."
    for key in sorted(key for key in applied if key.startswith(prefix)):
        value = applied[key]
        if isinstance(value, int | float) and not isinstance(value, bool):
            name = key[len(prefix) :]
            return name, value, {key: value}
    return None


def values(value: float) -> tuple[Any, ...]:
    """Three legal values of a declared knob, scaled by its own type."""
    if isinstance(value, int):
        return (value, value + 1, max(1, value - 1))
    return (value, value * 2, value / 2)


def decide(
    *,
    invariant: bool,
    fits: bool | None,
    control: bool | None,
    knob: bool | None,
    refused: str | None = None,
) -> tuple[str, str]:
    """The verdict and what decided it, from TODO98 §3's decision table.

    Args:
        invariant: Whether L-a held on the law's case.
        fits: Whether some admissible setting satisfied the law's criterion;
            ``None`` when no grid point was priced (all killed or refused).
        control: Whether the mechanism-removed fit satisfied the criterion;
            ``None`` when no control ran.
        knob: Whether L-c's knob moved the fit; ``None`` when not measured.
        refused: The declaration that refuses the cell, or the cost that
            killed every setting.

    Returns:
        The row's state and the step that decided it.
    """
    table = (
        (refused is not None, "refused", refused or ""),
        (not invariant, "defect (invariant)", "l-a invariant"),
        (fits is None, "defect-or-gap (mechanism)", "no priced grid point"),
        (fits is False, "defect-or-gap (mechanism)", "l-b fit"),
        (control is None, "unproven control", "no control ran"),
        (control is True, "test defect", CONTROL_REACHES),
        (knob is None, "unproven control", "the law records no knob on its axis"),
        (knob is False, "declaration defect", "l-c knob is inert"),
    )
    for decided, state, reason in table:
        if decided:
            return state, reason
    return "works", "l-b + control + l-c"
