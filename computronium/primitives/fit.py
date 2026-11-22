"""TODO98's law instruments: the carrier digest and the signal fit.

The six axes split by what their laws transform. A *carrier* law (substrate,
geometry, dynamics, plasticity) transforms a value that flows through the
cell, so its test is a digest against the axis's declared neutral companion:
equal digests mean the law *is* its companion. A *signal* law (credit,
update) transforms the learning channel, so its test is a deterministic fit
on the family's declared shape: 16 samples, at most 200 optimizer steps, at
three learning rates. The fit must reach a tenth of its untrained loss under
some legal setting, and the same fit must fail with the channel cut. A fit
that passes with the channel cut measures the optimizer: that is a test
defect.

Knob binding is not a test here: a knob that moves nothing at one box is a
coordinate, and the search space discovers it at the cost it already pays.

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
    from computronium.experiment.schema.axis import LawKind
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
    "Removal",
    "bound",
    "cell",
    "control",
    "coordinate",
    "decide",
    "family",
    "kind",
    "ladder",
    "measure",
    "problem",
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


class FitError(RuntimeError):
    """The fit could not run: the cell refuses its batch, or the step raises."""


@dataclass(frozen=True, slots=True)
class Removal:
    """A carrier law's removal reading: its step and its companion's.

    The companion is the axis's declared neutral element, so a differ is the
    law's own mechanism; an equal pair says the law *is* its companion, a
    silent pair says the case gave the law nothing to transform, and
    ``baseline`` says the law is the declared neutral element itself.
    """

    digest: str
    companion: str
    silent: bool = False
    baseline: bool = False

    @property
    def differs(self) -> bool:
        """The law's step differs from its declared companion's."""
        return self.digest != self.companion


def kind(spec: PrimitiveSpec) -> LawKind:
    """The fork's class: a carrier law transforms a value, a signal a channel."""
    from computronium.experiment.schema.axis import axis_kind

    return axis_kind(spec.axis)


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
    from computronium.experiment.sec_loop import _AXIS_DEFAULTS, _coordinate
    from computronium.experiment.sec_pilot import BASE_BOXES

    box = BASE_BOXES[family(spec)]
    axes = dict(_AXIS_DEFAULTS)
    if box.base_coordinate:
        axes.update(box.base_coordinate)
    axes[spec.axis] = spec.id.rsplit(".", 1)[-1]
    declared = _coordinate(axes)
    if lr is None:
        return declared
    return replace(declared, params={**declared.params, "update.step_size": lr})


def ladder(spec: PrimitiveSpec) -> list[tuple[str, tuple[float, float, str]]]:
    """The law's own declared knob grid: (knob, (min, max, scale)).

    Returns the intersection of:
    - The law's identity card ``approximation_parameters`` (what the law reads)
    - The axis spec's ``accepted_params`` (what composition may pass)
    - The harvested hyperparameter domain (what the search space declares)

    Each entry is a 3-tuple: (knob_name, (min_value, max_value, scale)).
    The scale is "log" or "linear" as declared in the hyperparameter domain.
    """
    from importlib import import_module
    from computronium.core.identity_card import AlgorithmIdentityCard
    from computronium.experiment.schema import AXES_REGISTRIES
    from computronium.experiment.schema.axis import StructuralAxis
    from computronium.experiment.schema.harvest import harvest_schema

    # 1. Law's declared approximation parameters (from identity card)
    ontology_class_path = getattr(spec, "ontology_class", None)
    card: AlgorithmIdentityCard | None = None
    if ontology_class_path and isinstance(ontology_class_path, str):
        try:
            module_path, _, class_name = ontology_class_path.rpartition(".")
            module = import_module(module_path)
            ontology_class = getattr(module, class_name, None)
            if ontology_class is not None:
                card = getattr(ontology_class, "IDENTITY_CARD", None)
        except Exception:
            pass
    elif ontology_class_path is not None:
        # Already a class object
        card = getattr(ontology_class_path, "IDENTITY_CARD", None)
    law_params = set(card.approximation_parameters) if card else set()

    # 2. Axis's accepted parameters (what composition may pass)
    axis_spec = AXES_REGISTRIES[StructuralAxis(spec.axis)].get(
        spec.id.rsplit(".", 1)[-1]
    )
    accepted = set(axis_spec.accepted_params) if axis_spec else set()

    # 3. Harvested hyperparameter domain (what the search space declares)
    schema = harvest_schema()
    domain: dict[str, tuple[float, float, str]] = {}
    for hp in schema.hyperparameters:
        if hp.domain is not None:
            # Domain format: Domain(members=...) for categorical, or Domain(lo=..., hi=..., scale=...) for continuous
            if hp.domain.members is not None:
                # Categorical: use the members as discrete points
                # For simplicity, use the first and last as min/max with linear scale
                members = list(hp.domain.members)
                if len(members) >= 2:
                    try:
                        domain[hp.name] = (float(members[0]), float(members[-1]), "linear")
                    except (ValueError, TypeError):
                        pass
            elif hp.domain.lo is not None and hp.domain.hi is not None:
                # Continuous domain
                scale = "log" if hp.domain.scale and hp.domain.scale.value == "log" else "linear"
                domain[hp.name] = (float(hp.domain.lo), float(hp.domain.hi), scale)

    # Intersection: law reads ∩ axis accepts ∩ domain declares
    knobs = law_params & accepted & set(domain.keys())
    return [(knob, domain[knob]) for knob in sorted(knobs)]


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


def _companion(
    spec: PrimitiveSpec, declared: Coordinate, seed: int = 0
) -> ComposedCell:
    """The law's cell with its axis replaced by the declared neutral element.

    The neutral element is the base box's own value (``feedforward``,
    ``instantaneous``, ``digital``, ``null``), so the removal is the one the
    repository already declares, not a per-axis table here. The companion is
    the declared coordinate for those six axes: its own structural params are
    recomputed, not inherited from the law's axis, where they would be dead
    configuration the composer refuses by name.
    """
    from computronium.experiment.sec_loop import _AXIS_DEFAULTS, _coordinate

    axes = {axis: getattr(declared, axis) for axis in cases.AXES}
    axes[spec.axis] = _AXIS_DEFAULTS[spec.axis]
    return cell(spec, _coordinate(axes), seed)


def _summary(
    spec: PrimitiveSpec, composed: ComposedCell, seed: int = 0
) -> tuple[str, bool]:
    """The digest of the law's reference step inside ``composed``, and silence.

    Silence means the step produced no weights, no activations and no tensor
    state: a law the case gives nothing to transform.
    """
    from computronium.acceleration.parity import digest

    case = cases.build_case(spec, "", {}, seed, cell=composed.config)
    result = cases.step(spec, case)
    silent = not (
        result.weights
        or result.activations
        or any(isinstance(value, torch.Tensor) for value in result.state.values())
    )
    return digest(result), silent


def bound(spec: PrimitiveSpec, declared: Coordinate, seed: int = 0) -> Removal:
    """A carrier law's removal: its step digest against its companion's.

    ``baseline`` records whether the law *is* the axis's declared neutral
    element: then its companion is itself by construction, and the row is the
    baseline's, not a law that failed to differ.
    """
    from computronium.experiment.sec_loop import _AXIS_DEFAULTS

    digest, silent = _summary(spec, cell(spec, declared, seed), seed)
    companion, _ = _summary(spec, control(spec, declared, seed), seed)
    baseline = getattr(declared, spec.axis) == _AXIS_DEFAULTS[spec.axis]
    return Removal(digest=digest, companion=companion, silent=silent, baseline=baseline)


def control(spec: PrimitiveSpec, declared: Coordinate, seed: int = 0) -> ComposedCell:
    """The same cell with the law's mechanism removed.

    A carrier law's axis is replaced by its declared neutral companion — a
    geometry by ``feedforward``, a settle by ``instantaneous``, a substrate by
    ``digital``, a plasticity law by ``null`` — because each of those laws is a
    mechanism *over* its companion, and the companion is the removal the
    repository already declares. A signal law's channel is cut in place: a
    credit's pseudo-gradient is zeroed and an update's step is identity.

    The replacement is a recipe, not a parameter patch: the pipeline rebuilds
    a geometry's weights each step, so zeroing them in place is undone at the
    first step (measured: a zeroed nca cell trained to the same loss).
    """
    if kind(spec) == "carrier":
        return _companion(spec, declared, seed)
    composed = cell(spec, declared, seed)
    match spec.axis:
        case "credit":
            composed.system.credit = _ZeroGradient(composed.system.credit)
        case "update":
            composed.system.update = _FrozenUpdate(composed.system.update)
        case other:
            msg = f"no control for signal axis {other!r}"
            raise ValueError(msg)
    return composed


def decide(
    *,
    law_kind: LawKind,
    invariant: bool,
    removal: Removal | None = None,
    fits: bool | None = None,
    control: bool | None = None,
    refused: str | None = None,
) -> tuple[str, str]:
    """The verdict and what decided it: one question per law.

    A carrier law is asked whether its step differs from the axis's declared
    neutral companion. A signal law is asked whether its cell trains and its
    cut-channel control does not. Knob binding is not a test here: a knob
    that moves nothing at one box is a coordinate, and the search space
    discovers it at the cost it already pays (TODO98 §3).

    Args:
        law_kind: Which instrument the law's axis declares.
        invariant: Whether L-a held on the law's case.
        removal: The carrier law's digest against its companion's.
        fits: Whether some admissible setting satisfied the law's criterion;
            ``None`` when no grid point was priced (all killed or refused).
        control: Whether the mechanism-removed fit satisfied the criterion;
            ``None`` when no control ran.
        refused: The declaration that refuses the cell, or the cost that
            killed every setting.

    Returns:
        The row's state and the step that decided it.
    """
    if refused is not None:
        return "refused", refused
    if not invariant:
        return "defect (invariant)", "l-a invariant"
    return (
        _carrier_verdict(removal)
        if law_kind == "carrier"
        else _signal_verdict(fits, control)
    )


def _carrier_verdict(removal: Removal | None) -> tuple[str, str]:
    """The carrier row: a differing digest is its mechanism, an equal one is not."""
    if removal is None:
        return "defect-or-gap (mechanism)", "no companion digest"
    if removal.baseline:
        return "inert", "the law is the axis's declared neutral element"
    if removal.silent:
        return "defect-or-gap (mechanism)", "the step has nothing to transform"
    if not removal.differs:
        return "inert", "the law is its companion"
    return "works", "l-a + digest"


def _signal_verdict(fits: bool | None, control: bool | None) -> tuple[str, str]:
    """The signal row: a fit that survives its cut channel is a test defect."""
    if fits is None:
        return "defect-or-gap (mechanism)", "no priced grid point"
    if not fits:
        return "defect-or-gap (mechanism)", "l-b fit"
    if control is None:
        return "defect-or-gap (mechanism)", "no control ran"
    if control:
        return "test defect", CONTROL_REACHES
    return "works", "l-b + control"
