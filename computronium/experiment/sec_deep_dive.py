"""S4: the deep dive the map chooses — one claim at one box (TODO95 P4/P5).

The census ranked the axes; the interaction slice measured which pair changes
together. Neither can say whether the surprising bound row — the measured cell
that sits at the bar's edge — is a defect probe or a primitive one knob away
from training. The deep dive is chosen by the map: the bound, non-swapped row
with the smallest margin over the bar becomes one factor-ready primitive.

The comparison is a 3-point ladder on the primitive's primary knob (the declared
default and its two decade neighbours), then five paired seeds of the best rung
against the primitive's own default at the matched base box. The margin is
pre-registered before the first seed, so the claim is fixed-n and cannot be
stopped early (TODO95 S4).

The claim reads the paired interval, never a seed: ``passes`` refuses a claim
whose box disagrees with the run, so a registration written for one box decides
nothing at another (TODO95 D2). A ladder whose best point is at the bar is a
capability gap — the knob is priced, not claimed — and an execution fact on any
rung or pair is a defect with its mechanism named.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path
from types import MappingProxyType
from typing import TYPE_CHECKING, Any, Final

from computronium.acceleration.spec import axis_segment
from computronium.experiment.sec_pilot import own_knob_params, BASE_BOXES, base_family
from computronium.validation.preregistration import (
    DEFAULT_ALPHA,
    EffectSizeRegistration,
    PairedComparison,
    ThresholdRegistration,
)

if TYPE_CHECKING:
    from collections.abc import Mapping

    from computronium.experiment.schema.coordinate import Schedule

__all__ = [
    "CLAIM_SEEDS",
    "LADDER_FACTORS",
    "LADDER_KNOBS",
    "MARGIN",
    "DeepDive",
    "DeepDiveCandidate",
    "LadderRung",
    "PairedCell",
    "best_rung",
    "candidate_box",
    "claim_verdict",
    "ladder_points",
    "load_registration",
    "preregister",
    "primary_knob",
    "select_candidate",
    "tuning_candidates",
]

#: The ladder's three points, as factors of the knob's declared default. A rung
#: that the validator refuses is a row with its trigger, never a hidden point.
LADDER_FACTORS: Final[tuple[float, ...]] = (0.1, 1.0, 10.0)

# Rung 1 best knob values for each credit (from TODO100 Rung 1 ladder on digits)
# Used to center the ladder around the known best value for Rung 2
RUNG1_BEST_KNOBS: Final[Mapping[str, float]] = MappingProxyType({
    "random_projections": 10.0,  # feedback_scale
    "local_contrastive": 100.0,  # readout_scale
    "thermodynamic_contrast": 0.1,  # beta
    "pc_alm": 0.5,  # beta
    "target_inversion": 10.0,  # feedback_scale
    "pepita": 0.05,  # feedback_scale
    "forward_tangent": 256.0,  # estimator_samples
    "score_function": 256.0,  # estimator_samples
    "zeroth_order": 0.01,  # fd_step
    "surrogate": 0.01,  # feedback_scale (no ladder, baseline)
    "local_goodness": 1.0,  # readout_error (boolean, True=1.0)
    "hybrid": 0.05,  # feedback_scale
    "local_supervision": 0.1,  # aux_head_scale
    "gradient": 0.01,  # feedback_scale (baseline)
})
#: Paired seeds per arm. Fixed before the first seed, so the claim is fixed-n
#: and cannot be stopped early (TODO95 S4).
CLAIM_SEEDS: Final[int] = 5
#: The smallest material effect at the accuracy ruler: one percentage point of
#: held-out samples. It is committed in the registration before the run.
MARGIN: Final[float] = 0.01
#: The primary knob of a deep dive, per axis, in preference order: the first
#: declared numeric knob of the primitive's own config is the one laddered. The
#: declaration names the knob; the default value stays the config classmethod's.
LADDER_KNOBS: Final[Mapping[str, tuple[str, ...]]] = MappingProxyType({
    "credit": (
        "feedback_scale",
        "beta",
        "readout_scale",
        "fd_step",
        "estimator_samples",
        "aux_head_scale",
        "lr",
    ),
    "dynamics": ("step_size", "max_steps"),
    "geometry": ("hidden_dim", "depth", "width"),
    "update": ("step_size", "momentum"),
    "plasticity": ("trace_decay",),
    "substrate": ("noise_level", "sparsity"),
})


def _val_acc(row: Mapping[str, Any]) -> float | None:
    value = (row.get("measurement") or {}).get("val_acc")
    return None if value is None else float(value)


def primary_knob(axis: str, primitive: str) -> tuple[str, float] | None:
    """The primitive's primary knob and its declared default, or ``None``.

    The knob is the first name in :data:`LADDER_KNOBS` that the primitive's own
    config classmethod declares as a positive number. A primitive with no such
    knob has no ladder and is not a deep dive: it is not factor-ready here.
    """
    params = own_knob_params(axis, primitive)
    for name in LADDER_KNOBS.get(axis, ()):
        key = f"{axis}.{name}"
        value = params.get(key)
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            continue
        if value > 0:
            return key, float(value)
    return None


@dataclass(frozen=True, slots=True)
class DeepDiveCandidate:
    """The surprising bound row: the cell the map sends to a deep dive."""

    primitive: str
    axis: str
    level: str
    val_acc: float
    margin: float
    knob: str
    default: float
    #: The row's screened box: its six axes, its structural params and the
    #: schedule. The pair's arms rebuild from it, so a row screened before
    #: the box carried its params has no dive (TODO97 S9c).
    box: dict[str, Any]
    walltime_s: float | None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _bound_candidate(
    primitive: str, row: Mapping[str, Any], bar: float
) -> DeepDiveCandidate | None:
    """One knobbed bound row above the bar, or ``None`` when it is not one.

    A row that refused, swapped, went inert, or measured at the bar is not a
    candidate: the bar already decided it, or the row re-measures the control.
    """
    if row.get("status") != "measured" or row.get("swapped"):
        return None
    if row.get("binding") != "bound":
        return None
    val_acc = _val_acc(row)
    if val_acc is None or val_acc <= bar:
        return None
    axis = axis_segment(str(row.get("axis", "")))
    level = primitive.rsplit(".", 1)[-1]
    knob = primary_knob(axis, level)
    if knob is None:
        return None
    return DeepDiveCandidate(
        primitive=primitive,
        axis=axis,
        level=level,
        val_acc=val_acc,
        margin=val_acc - bar,
        knob=knob[0],
        default=knob[1],
        box=dict(row.get("box") or {}),
        walltime_s=(row.get("resource") or {}).get("walltime_s"),
    )


def _bound_candidates(map_data: Mapping[str, Any]) -> list[DeepDiveCandidate]:
    bar = (map_data.get("inventory") or {}).get("bar")
    if bar is None:
        return []
    return [
        candidate
        for primitive, row in (map_data.get("primitives") or {}).items()
        if (candidate := _bound_candidate(str(primitive), row, float(bar))) is not None
    ]


def select_candidate(map_data: Mapping[str, Any]) -> DeepDiveCandidate | None:
    """The bound row with the smallest margin over the bar, with a knob.

    The map's ranking is the selection, never a second table (TODO95 P4).
    """
    rows = _bound_candidates(map_data)
    if not rows:
        return None
    return min(rows, key=lambda candidate: (candidate.margin, candidate.primitive))


def tuning_candidates(
    map_data: Mapping[str, Any], limit: int | None = 2
) -> tuple[DeepDiveCandidate, ...]:
    """The rows S9 ladders for the claim list: the largest margin over the bar.

    Walltime does not rank them: a cheap row and a costly row are compared by
    the margin their own family bar leaves, so the two added ladders are the
    rows with the most headroom (TODO97 S9). The base axis's own value
    re-measures the family's control, so it is not a tuning candidate.
    """
    base = map_data.get("base") or {}
    primitives = map_data.get("primitives") or {}
    rows = [
        candidate
        for candidate in _bound_candidates(map_data)
        if (primitives[candidate.primitive].get("box") or {}).get(candidate.axis)
        != base.get(candidate.axis)
    ]
    rows.sort(key=lambda candidate: (-candidate.margin, candidate.primitive))
    return tuple(rows if limit is None else rows[:limit])


def ladder_points(candidate: DeepDiveCandidate) -> tuple[tuple[float, float], ...]:
    """The three ladder points: each factor and the knob value it declares."""
    return tuple((factor, candidate.default * factor) for factor in LADDER_FACTORS)


@dataclass(frozen=True, slots=True)
class LadderRung:
    """One point of the ladder: its knob value, number and box."""

    factor: float
    value: float
    status: str  # measured | refused | defect
    val_acc: float | None
    walltime_s: float | None
    replay_hash: str | None
    box: dict[str, Any]
    reason: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class PairedCell:
    """One arm of the paired comparison: its seed, number and replay hash."""

    arm: str  # treatment | control
    factor: float
    seed: int
    status: str
    val_acc: float | None
    loss: float | None
    walltime_s: float | None
    replay_hash: str | None
    box: dict[str, Any]
    reason: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class DeepDive:
    """The record: the candidate, the ladder, the pair and the verdict."""

    candidate: DeepDiveCandidate
    rungs: tuple[LadderRung, ...]
    best: LadderRung | None
    cells: tuple[PairedCell, ...]
    paired: dict[str, Any] | None
    claim: dict[str, Any]
    verdict: str  # claim | coordinate | defect
    stop_reason: str
    walltime_s: float | None
    #: Whether the ladder moved the number: an inert knob is a capability gap,
    #: not a result about the axis (TODO95 D8).
    knob_binds: bool
    #: Whether the pair could carry error control. Identical arms measure a
    #: structurally zero difference, so the pair is marked, not reported.
    no_power: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "candidate": self.candidate.to_dict(),
            "ladder": [rung.to_dict() for rung in self.rungs],
            "best": None if self.best is None else self.best.to_dict(),
            "cells": [cell.to_dict() for cell in self.cells],
            "effect": self.paired,
            "claim": self.claim,
            "verdict": self.verdict,
            "stop_reason": self.stop_reason,
            "walltime_s": self.walltime_s,
            "knob_binds": self.knob_binds,
            "no_power": self.no_power,
        }


def best_rung(rungs: tuple[LadderRung, ...]) -> LadderRung | None:
    """The measured rung with the highest accuracy, or ``None`` when none ran.

    A refused or defective rung is not a point of the ladder's answer; ties go
    to the smallest factor, the point nearest the primitive's own default.
    """
    measured = [rung for rung in rungs if rung.status == "measured"]
    if not measured or any(rung.val_acc is None for rung in measured):
        return None
    return min(
        measured,
        key=lambda rung: (-(rung.val_acc or 0.0), rung.factor),
    )


def candidate_box(
    candidate: DeepDiveCandidate, factor: float, schedule: Schedule
) -> dict[str, Any]:
    """The box one arm trains at: the row's coordinate, its params too.

    One builder: the screen's own ``_box_summary`` reads the coordinate's six
    axes, its structural params and the schedule, so a registration and a pair
    compare the same fields (TODO97 S9c). The factor is the arm's ladder point,
    so the control arm's box is the row's own box.
    """
    from computronium.experiment.sec_loop import _box_summary, _deep_dive_coordinate

    return _box_summary(_deep_dive_coordinate(candidate, factor), schedule)


def claim_registration(
    candidate: DeepDiveCandidate, schedule: Schedule
) -> EffectSizeRegistration:
    """The pre-registered effect size threshold, written before the first paired seed.

    Uses Cohen's d (effect size) with per-task-family minimums (TODO99 #6).
    The box is the row's own coordinate, not the base schedule alone: a
    registration that declares a box decides only a run at that box, and a
    claim re-boxed between the ladder and the pair is refused by name
    (TODO95 D2, TODO97 S9c).
    """
    return EffectSizeRegistration.for_task_family(
        claim=(
            f"tuning {candidate.knob} on {candidate.primitive} improves val_acc "
            f"with Cohen's d >= family minimum at the {schedule.task_id} base"
        ),
        metric="val_acc",
        task_id=schedule.task_id,
        alpha=DEFAULT_ALPHA,
        min_seeds=CLAIM_SEEDS,
        created=date.today().isoformat(),
        box=candidate_box(candidate, 1.0, schedule),
    )


def preregister(
    map_data: Mapping[str, Any],
    schedule: Schedule,
    path: Path,
) -> ThresholdRegistration:
    """Register the claim the map's candidate names, before any run.

    Raises:
        ValueError: When the map sends no row to a deep dive.
    """
    candidate = select_candidate(map_data)
    if candidate is None:
        msg = "no surprising bound row with a declared knob in this map"
        raise ValueError(msg)
    registration = claim_registration(candidate, schedule)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(registration.to_dict(), indent=2), encoding="utf-8")
    return registration


def load_registration(
    path: Path, box: Schedule | Mapping[str, Any]
) -> ThresholdRegistration | EffectSizeRegistration | None:
    """The committed registration for this box, or ``None`` when it refuses.

    The box is the coordinate's own (its axes and structural params too), so a
    registration committed for another coordinate is refused before the first
    cell (TODO97 S9c). A session that cannot name its claim before its first
    cell is a budget leak: the run refuses instead of comparing five
    unregistered seeds.

    Supports both ThresholdRegistration (absolute margin) and EffectSizeRegistration (Cohen's d).
    """
    if not path.exists():
        return None
    # Try EffectSizeRegistration first (new format), fall back to ThresholdRegistration
    try:
        registration = EffectSizeRegistration.load(path)
    except (KeyError, ValueError):
        registration = None
    if registration is not None and registration.metric == "val_acc" and registration.box_mismatch(box) is None:
        return registration

    try:
        registration = ThresholdRegistration.load(path)
    except (KeyError, ValueError):
        return None
    if registration.metric == "val_acc" and registration.box_mismatch(box) is None:
        return registration
    return None


def claim_verdict(
    paired: PairedComparison | None,
    registration: ThresholdRegistration | EffectSizeRegistration,
    box: Schedule | Mapping[str, Any],
) -> str:
    """The claim when the paired CI clears the registered margin/effect size, else a row.

    ``passes`` refuses a claim at another box and a CI that includes the
    margin: the pair is then a coordinate about the knob, not a verdict. The box
    is the coordinate's own (its axes and structural params), not the schedule
    alone, so the registration and the run compare the same fields (TODO97 S9c).
    """
    if paired is None:
        return "coordinate"
    if isinstance(registration, EffectSizeRegistration):
        return (
            "claim"
            if paired.passes_effect_size(registration, box=box)
            else "coordinate"
        )
    return "claim" if paired.passes(registration, box=box) else "coordinate"


# Credit-specific dynamics and geometry overrides
CREDIT_DYNAMICS_OVERRIDE: Final[Mapping[str, str]] = MappingProxyType({
    "thermodynamic_contrast": "energy_minimization",
    "pc_alm": "pc_alm",
})

CREDIT_GEOMETRY_OVERRIDE: Final[Mapping[str, str]] = MappingProxyType({
    "surrogate": "routing",
})

_CREDIT_WITH_ENERGY_MIN: Final[set[str]] = {"thermodynamic_contrast", "pc_alm"}


def _credit_axes(credit: str) -> dict[str, str]:
    """Build axes dict for a credit, applying overrides."""
    from computronium.experiment.sec_loop import _AXIS_DEFAULTS

    axes = {name: _AXIS_DEFAULTS[name] for name in _AXIS_DEFAULTS}
    axes["credit"] = credit
    if credit in CREDIT_DYNAMICS_OVERRIDE:
        axes["dynamics"] = CREDIT_DYNAMICS_OVERRIDE[credit]
    if credit in CREDIT_GEOMETRY_OVERRIDE:
        axes["geometry"] = CREDIT_GEOMETRY_OVERRIDE[credit]
    return axes


def _add_credit_config_params(
    factory: Any,
    credit: str,
    accepted_params: frozenset[str],
    ctx: Any,
    structural_params: dict[str, Any],
) -> None:
    """Add credit config params to structural_params if accepted and available."""
    from computronium.experiment.legality.dsl import evaluate

    try:
        config = factory()
    except TypeError:
        return

    for field_name in dir(config):
        _process_config_field(
            field_name, config, credit, accepted_params, ctx, structural_params, evaluate
        )


def _process_config_field(
    field_name: str,
    config: Any,
    credit: str,
    accepted_params: frozenset[str],
    ctx: Any,
    structural_params: dict[str, Any],
    evaluate: Any,
) -> None:
    """Process a single config field for structural params."""
    from computronium.ontology.credit import CreditAssignmentConfig

    if not field_name.startswith("_") and field_name in accepted_params:
        hp_spec = CreditAssignmentConfig.hyperparameters(credit).get(field_name, {})
        avail_pred = hp_spec.get("availability")
        is_available = True
        if avail_pred is not None:
            is_available = evaluate(avail_pred, ctx)
        if is_available:
            value = getattr(config, field_name)
            if not callable(value):
                structural_params[f"credit.{field_name}"] = value


def _credit_structural_params(credit: str, axes: dict[str, str]) -> dict[str, Any]:
    """Get structural params for a credit (only accepted AND available)."""
    from computronium.experiment.schema.axis import StructuralAxis, get_axis_spec
    from computronium.experiment.schema.coordinate import Coordinate
    from computronium.experiment.schema.harvest import CoordinateContext
    from computronium.ontology.credit import CreditAssignmentConfig

    credit_spec = get_axis_spec(StructuralAxis.CREDIT, credit)
    accepted_params = credit_spec.accepted_params if credit_spec else frozenset()

    coord = Coordinate(
        substrate=axes["substrate"],
        geometry=axes["geometry"],
        dynamics=axes["dynamics"],
        plasticity=axes["plasticity"],
        credit=credit,
        update=axes["update"],
        params={},
    )
    ctx = CoordinateContext(coord)

    factory = getattr(CreditAssignmentConfig, credit, None)
    structural_params = {
        "update.step_size": 0.01,
        "geometry.hidden_dim": 128,
        "geometry.depth": 2,
    }

    if callable(factory):  # ruff: ignore[complex-structure, too-many-nested-blocks, redefined-argument-from-local]
        _add_credit_config_params(
            factory, credit, accepted_params, ctx, structural_params
        )

    if credit in _CREDIT_WITH_ENERGY_MIN:
        structural_params.update({
            "dynamics.max_steps": 10,
            "dynamics.step_size": 0.1,
        })
    return structural_params


def _credit_base_box(credit: str, task_id: str = "mnist") -> dict[str, Any]:
    """The base box for a credit on a task family (full coordinate box with axes and defaults)."""
    from computronium.experiment.sec_pilot import base_schedule

    schedule = base_schedule(task_id, "auto")
    if schedule is None:
        raise ValueError(f"{task_id} declares no base box")

    # Get family base coordinate for structural axes
    family = base_family(task_id)
    base_coord = BASE_BOXES.get(family).base_coordinate if family and BASE_BOXES.get(family) else None

    # Start with credit-specific axes, then override structural axes from base_coordinate
    axes = _credit_axes(credit)
    if base_coord:
        structural_axes = {"substrate", "geometry", "dynamics", "plasticity"}
        for ax_name in structural_axes:
            if ax_name in base_coord:
                axes[ax_name] = base_coord[ax_name]

    structural_params = _credit_structural_params(credit, axes)

    box = schedule.to_dict()
    box["device"] = "cuda"
    box["task"] = task_id
    box.update(axes)
    box.update(structural_params)
    return box


# Primary knob for each credit (from TODO100 Rung 1 ladder results)
CREDIT_PRIMARY_KNOB: Final[Mapping[str, str]] = MappingProxyType({
    "random_projections": "feedback_scale",
    "local_contrastive": "readout_scale",
    "thermodynamic_contrast": "beta",
    "pc_alm": "beta",
    "target_inversion": "feedback_scale",
    "pepita": "feedback_scale",
    "forward_tangent": "estimator_samples",
    "score_function": "estimator_samples",
    "zeroth_order": "fd_step",
    "surrogate": "feedback_scale",
    "local_goodness": "readout_error",
    "hybrid": "feedback_scale",
    "local_supervision": "aux_head_scale",
    "gradient": "feedback_scale",
})


def _credit_knob_default(credit: str) -> tuple[str, float] | None:
    """Get the primary knob and its default for a credit from the config factory."""
    from computronium.experiment.sec_pilot import own_knob_params
    from computronium.ontology.credit import CreditAssignmentConfig

    # Use the declared primary knob for this credit
    primary_knob_name = CREDIT_PRIMARY_KNOB.get(credit)
    if primary_knob_name is None:
        return None

    # Check the config factory for the default value
    factory = getattr(CreditAssignmentConfig, credit, None)
    if callable(factory):
        try:
            config = factory()
            if hasattr(config, primary_knob_name):
                value = getattr(config, primary_knob_name)
                if isinstance(value, bool):
                    # For boolean knobs (like readout_error), return as float 1.0/0.0
                    return f"credit.{primary_knob_name}", 1.0 if value else 0.0
                if isinstance(value, (int, float)) and value > 0:
                    return f"credit.{primary_knob_name}", float(value)
        except TypeError:
            pass

    # Fallback: try own_knob_params
    params = own_knob_params("credit", credit)
    key = f"credit.{primary_knob_name}"
    value = params.get(key)
    if isinstance(value, (int, float)) and value > 0:
        return key, float(value)

    return None


async def run_rung2_comparison(  # ruff: ignore[too-many-locals]
    credit: str,
    registration_path: Path,
    task_id: str = "mnist",
    n_seeds: int = 5,
    device: str = "auto",
    semaphore_limit: int = 2,
) -> dict[str, Any]:
    """Run Rung 2: paired comparison of credit at best box vs gradient at base box.

    This is the TODO100 Rung 2 experiment: each viable credit at its best declared box
    (from Rung 1 ladder) paired against gradient (euclidean update baseline) at the
    matched base box. n_seeds=5 per arm.
    """
    import asyncio
    import time
    from dataclasses import replace

    from computronium.experiment.sec_deep_dive import (
        CREDIT_PRIMARY_KNOB,
        RUNG1_BEST_KNOBS,
        DeepDiveCandidate,
        candidate_box,
        claim_verdict,
        load_registration,
    )
    from computronium.experiment.sec_loop import (
        _measure,
        base_schedule,
        screen_coordinate,
    )
    from computronium.validation.preregistration import (
        EffectSizeRegistration,
        ThresholdRegistration,
        paired_comparison,
    )

    schedule = base_schedule(task_id, device)
    if schedule is None:
        raise ValueError(f"{task_id} declares no base box")

    # Try loading registration with a minimal box first to get the registration object
    temp_box = schedule.to_dict()
    temp_box["device"] = "cuda"
    temp_box["task"] = task_id
    registration = load_registration(registration_path, temp_box)
    if registration is None:
        # Try loading directly
        try:
            registration = ThresholdRegistration.load(registration_path)
        except (KeyError, ValueError):
            registration = EffectSizeRegistration.load(registration_path)

    # Get the credit's primary knob and Rung 1 best value
    primary_knob_name = CREDIT_PRIMARY_KNOB.get(credit)
    if primary_knob_name is None:
        return {"credit": credit, "status": "no_primary_knob", "skipped": True}

    rung1_best = RUNG1_BEST_KNOBS.get(credit)
    if rung1_best is None:
        return {"credit": credit, "status": "no_rung1_best", "skipped": True}

    knob_key = f"credit.{primary_knob_name}"

    print(f"Running Rung 2 for {credit}: {primary_knob_name}={rung1_best} vs gradient")

    started = time.monotonic()

    # Build treatment coordinate: credit at Rung 1 best knob value (with credit's own defaults)
    treatment_base_box = _credit_base_box(credit, task_id)
    treatment_box = dict(treatment_base_box)
    treatment_box[knob_key] = rung1_best
    treatment_coord = screen_coordinate(treatment_box, "credit", credit)

    # Build control coordinate: gradient at its own base box (with gradient's defaults)
    control_base_box = _credit_base_box("gradient", task_id)
    control_coord = screen_coordinate(control_base_box, "credit", "gradient")

    # Run paired comparison: n_seeds per arm
    print(
        f"Running {n_seeds} paired seeds (treatment={credit}@{primary_knob_name}={rung1_best}, control=gradient)..."
    )

    cells = []
    for seed in range(n_seeds):
        for arm, coord in (("treatment", treatment_coord), ("control", control_coord)):
            measured = await asyncio.to_thread(
                _measure, coord, replace(schedule, seed=seed, n_seeds=1)
            )
            from computronium.experiment.sec_deep_dive import PairedCell

            cells.append(
                PairedCell(
                    arm=arm,
                    factor=1.0,  # Not a ladder factor
                    seed=seed,
                    status=measured["status"],
                    val_acc=measured["val_acc"],
                    loss=measured["loss"],
                    walltime_s=measured["walltime_s"],
                    replay_hash=measured["replay_hash"],
                    box=measured["box"],
                    reason=measured["reason"],
                )
            )

    failed = next((cell for cell in cells if cell.status == "defect"), None)
    if failed is not None:
        return {
            "credit": credit,
            "cells": [cell.to_dict() for cell in cells],
            "verdict": "defect",
            "stop_reason": f"rung 2: the {failed.arm} arm at seed {failed.seed} is an execution fact: {failed.reason}",
            "walltime_s": time.monotonic() - started,
        }

    # Evaluate paired comparison
    treatments = [cell for cell in cells if cell.arm == "treatment"]
    controls = [cell for cell in cells if cell.arm == "control"]
    identical = all(
        treatment.val_acc == control.val_acc
        for treatment, control in zip(treatments, controls, strict=True)
    )
    if identical:
        return {
            "credit": credit,
            "cells": [cell.to_dict() for cell in cells],
            "verdict": "coordinate",
            "stop_reason": "rung 2: the arms are identical at every seed — no difference detected",
            "walltime_s": time.monotonic() - started,
            "no_power": True,
        }

    paired = paired_comparison(
        [float(cell.val_acc or 0.0) for cell in treatments],
        [float(cell.val_acc or 0.0) for cell in controls],
        seed=schedule.seed,
    )

    # Use the treatment box for box mismatch check (registration box)
    base_box = dict(registration.box)
    verdict = claim_verdict(
        paired,
        registration,
        candidate_box(
            DeepDiveCandidate(
                primitive=f"primitive.credit_assignment.{credit}",
                axis="credit",
                level=credit,
                val_acc=0.0,
                margin=0.0,
                knob=knob_key,
                default=base_box.get(knob_key, 0.01),
                box=base_box,
                walltime_s=None,
            ),
            1.0,
            schedule,
        ),
    )

    print(
        f"Paired comparison: mean_diff={paired.mean_diff:.4f}, CI=[{paired.ci_lower:.4f}, {paired.ci_upper:.4f}], d={paired.cohens_dz:.4f}, p={paired.p_value:.4f}"
    )
    print(f"Verdict: {verdict}")

    # Calculate treatment and control mean val_acc
    treatment_mean = sum(float(cell.val_acc or 0.0) for cell in treatments) / len(
        treatments
    )
    control_mean = sum(float(cell.val_acc or 0.0) for cell in controls) / len(controls)

    return {
        "credit": credit,
        "treatment_mean_val_acc": treatment_mean,
        "control_mean_val_acc": control_mean,
        "cells": [cell.to_dict() for cell in cells],
        "effect": {
            "n": paired.n,
            "mean_diff": paired.mean_diff,
            "ci_lower": paired.ci_lower,
            "ci_upper": paired.ci_upper,
            "p_value": paired.p_value,
            "cohens_dz": paired.cohens_dz,
        },
        "verdict": verdict,
        "stop_reason": (
            "rung 2: five paired seeds at best box; the CI clears the registered margin"
            if verdict == "claim"
            else "rung 2: five paired seeds at best box; the effect sits inside the registered margin"
        ),
        "walltime_s": time.monotonic() - started,
    }


async def run_credit_deep_dive(  # ruff: ignore[too-many-locals]
    credit: str,
    registration_path: Path,
    task_id: str = "mnist",
    n_seeds: int = 5,
    device: str = "auto",
    semaphore_limit: int = 2,
) -> dict[str, Any]:
    """Run the deep dive for a specific credit at its best box.

    This is the Rung 2 experiment: 3-point ladder on the credit's primary knob,
    then n_seeds paired comparison at the best ladder point vs the credit's default.
    """
    import asyncio
    import time

    from computronium.experiment.sec_deep_dive import (
        DeepDiveCandidate,
        best_rung,
        candidate_box,
        claim_verdict,
        load_registration,
    )
    from computronium.experiment.sec_loop import (
        _ladder_async,
        _paired_cells_async,
        _task_bar,
        base_schedule,
    )
    from computronium.validation.preregistration import paired_comparison

    # Load registration
    base_box = _credit_base_box(credit, task_id)
    schedule = base_schedule(task_id, device)
    if schedule is None:
        raise ValueError(f"{task_id} declares no base box")

    registration = load_registration(registration_path, base_box)
    if registration is None:
        raise ValueError(
            f"No valid pre-registration at {registration_path} for this box"
        )

    # Get the credit's primary knob and default
    knob_info = _credit_knob_default(credit)
    if knob_info is None:
        # No knob - this is a baseline credit (gradient, surrogate, local_supervision)
        # Run paired comparison directly at the best box (which is the default box)
        print(
            f"Credit {credit} has no primary knob; running paired comparison at default box"
        )
        # For now, skip credits without knobs
        return {"credit": credit, "status": "no_knob", "skipped": True}

    knob_key, default_value = knob_info
    knob_name = knob_key.split(".", 1)[
        1
    ]  # e.g., "credit.feedback_scale" -> "feedback_scale"

    # Create candidate for the deep dive logic
    candidate = DeepDiveCandidate(
        primitive=f"primitive.credit_assignment.{credit}",
        axis="credit",
        level=credit,
        val_acc=0.0,  # Will be measured
        margin=0.0,
        knob=knob_key,
        default=default_value,
        box=base_box,
        walltime_s=None,
    )

    started = time.monotonic()

    # Run 3-point ladder
    print(
        f"Running 3-point ladder for {credit} on {knob_name} (default={default_value})"
    )
    rungs = await _ladder_async(candidate, schedule, asyncio.Semaphore(semaphore_limit))

    best = best_rung(tuple(rungs))
    bar = _task_bar(task_id)
    if best is None or (bar is not None and (best.val_acc or 0.0) <= bar.value):
        reason = (
            "rung 2: no ladder point clears the bar at this box; the knob is "
            "priced, not claimed (a capability gap)"
        )
        return {
            "credit": credit,
            "ladder": [rung.to_dict() for rung in rungs],
            "best": None if best is None else best.to_dict(),
            "verdict": "coordinate",
            "stop_reason": reason,
            "walltime_s": time.monotonic() - started,
        }

    # Run paired comparison at best ladder point
    print(
        f"Best ladder point: factor={best.factor}, value={best.value}, val_acc={best.val_acc}"
    )
    print(f"Running {n_seeds} paired seeds at best point...")
    cells = await _paired_cells_async(
        candidate, schedule, best.factor, asyncio.Semaphore(semaphore_limit)
    )

    failed = next((cell for cell in cells if cell.status == "defect"), None)
    if failed is not None:
        return {
            "credit": credit,
            "ladder": [rung.to_dict() for rung in rungs],
            "best": best.to_dict(),
            "cells": [cell.to_dict() for cell in cells],
            "verdict": "defect",
            "stop_reason": f"rung 4: the {failed.arm} arm at seed {failed.seed} is an execution fact: {failed.reason}",
            "walltime_s": time.monotonic() - started,
        }

    # Evaluate paired comparison
    treatments = [cell for cell in cells if cell.arm == "treatment"]
    controls = [cell for cell in cells if cell.arm == "control"]
    identical = all(
        treatment.val_acc == control.val_acc
        for treatment, control in zip(treatments, controls, strict=True)
    )
    if identical:
        return {
            "credit": credit,
            "ladder": [rung.to_dict() for rung in rungs],
            "best": best.to_dict(),
            "cells": [cell.to_dict() for cell in cells],
            "verdict": "coordinate",
            "stop_reason": "rung 4: the arms are identical at every seed — the knob does not bind at this box",
            "walltime_s": time.monotonic() - started,
            "no_power": True,
        }

    paired = paired_comparison(
        [float(cell.val_acc or 0.0) for cell in treatments],
        [float(cell.val_acc or 0.0) for cell in controls],
        seed=schedule.seed,
    )
    verdict = claim_verdict(
        paired, registration, candidate_box(candidate, 1.0, schedule)
    )

    print(
        f"Paired comparison: mean_diff={paired.mean_diff:.4f}, CI=[{paired.ci_lower:.4f}, {paired.ci_upper:.4f}], d={paired.cohens_dz:.4f}, p={paired.p_value:.4f}"
    )
    print(f"Verdict: {verdict}")

    return {
        "credit": credit,
        "ladder": [rung.to_dict() for rung in rungs],
        "best": best.to_dict(),
        "cells": [cell.to_dict() for cell in cells],
        "effect": {
            "n": paired.n,
            "mean_diff": paired.mean_diff,
            "ci_lower": paired.ci_lower,
            "ci_upper": paired.ci_upper,
            "p_value": paired.p_value,
            "cohens_dz": paired.cohens_dz,
        },
        "verdict": verdict,
        "stop_reason": (
            "rung 4: five paired seeds at the base box; the CI clears the registered margin"
            if verdict == "claim"
            else "rung 4: five paired seeds at the base box; the effect sits inside the registered margin"
        ),
        "walltime_s": time.monotonic() - started,
    }


def main() -> None:  # ruff: ignore[too-many-statements]
    """SEC deep dive: pre-register or run a credit's deep dive.

    Pre-register:
        uv run python -m computronium.experiment.sec_deep_dive preregister \
            --map results/sec/map.json --out configs/preregistrations/sec_deep_dive.json

    Run for a specific credit (Rung 2):
        uv run python -m computronium.experiment.sec_deep_dive run \
            --credit random_projections --family vision \
            --registration configs/preregistrations/sec_credit_random_projections.json \
            --n-seeds 5 --async
    """
    import argparse
    import asyncio
    import json

    from computronium.experiment.sec_loop import base_schedule

    parser = argparse.ArgumentParser(
        description="SEC S4 - pre-register or run deep dive"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Pre-register command
    prereg_parser = subparsers.add_parser(
        "preregister", help="Pre-register the deep dive claim from map"
    )
    prereg_parser.add_argument(
        "--map", type=Path, default=Path("results/sec/map.json"), help="Map document"
    )
    prereg_parser.add_argument(
        "--out", type=Path, required=True, help="Registration file"
    )

    # Run command
    run_parser = subparsers.add_parser(
        "run", help="Run deep dive for a specific credit (Rung 2)"
    )
    run_parser.add_argument(
        "--credit",
        type=str,
        required=True,
        help="Credit to run (e.g., random_projections)",
    )
    run_parser.add_argument(
        "--family",
        type=str,
        default="vision",
        help="Task family (vision, tabular, graph, etc.)",
    )
    run_parser.add_argument(
        "--registration", type=Path, required=True, help="Pre-registration file"
    )
    run_parser.add_argument(
        "--n-seeds", type=int, default=5, help="Number of paired seeds"
    )
    run_parser.add_argument(
        "--async",
        action="store_true",
        dest="use_async",
        help="Use async parallel execution",
    )
    run_parser.add_argument(
        "--device", type=str, default="auto", help="Device (auto, cpu, cuda)"
    )
    run_parser.add_argument(
        "--semaphore", type=int, default=2, help="Max concurrent GPU tasks"
    )
    run_parser.add_argument("--out", type=Path, help="Output file for results")

    args = parser.parse_args()

    if args.command == "preregister":
        map_data = json.loads(args.map.read_text())
        task_id = str((map_data.get("base") or {}).get("task") or "mnist")
        schedule = base_schedule(task_id, "auto")
        if schedule is None:
            msg = f"{task_id} declares no base box; the claim is refused"
            raise SystemExit(msg)
        registration = preregister(map_data, schedule, args.out)
        print(f"Claim registered: {registration.claim}")
        print(
            f"  margin {getattr(registration, 'threshold', getattr(registration, 'min_d', 'N/A'))}, "
            f"alpha {registration.alpha}, "
            f"n_max {registration.min_seeds} -> {args.out}"
        )

    elif args.command == "run":
        # Map family to task_id
        family_to_task = {
            "vision": "mnist",
            "tabular": "iris",
            "graph": "cora",
            "sequence": "sequential_mnist",
            "continual": "split_mnist",
            "rl": "cartpole",
        }
        task_id = family_to_task.get(args.family, args.family)

        result = asyncio.run(
            run_rung2_comparison(
                credit=args.credit,
                registration_path=args.registration,
                task_id=task_id,
                n_seeds=args.n_seeds,
                device=args.device,
                semaphore_limit=args.semaphore,
            )
        )

        if args.out:
            import json

            args.out.parent.mkdir(parents=True, exist_ok=True)
            args.out.write_text(json.dumps(result, indent=2))
            print(f"Results written to {args.out}")

        # Print summary
        print(f"\n=== Rung 2 Result for {args.credit} ===")
        print(f"Verdict: {result['verdict']}")
        print(f"Stop reason: {result['stop_reason']}")
        print(f"Walltime: {result.get('walltime_s', 0):.1f}s")
        if result.get("treatment_mean_val_acc") is not None:
            print(
                f"Treatment ({args.credit}) mean val_acc: {result['treatment_mean_val_acc']:.4f}"
            )
            print(
                f"Control (gradient) mean val_acc: {result['control_mean_val_acc']:.4f}"
            )
        if result.get("effect"):
            eff = result["effect"]
            print(
                f"Effect: mean_diff={eff['mean_diff']:.4f}, CI=[{eff['ci_lower']:.4f}, {eff['ci_upper']:.4f}], d={eff['cohens_dz']:.4f}"
            )

        if result["verdict"] == "claim":
            print("✅ CLAIM CONFIRMED")
        elif result["verdict"] == "coordinate":
            print("📊 COORDINATE RESULT (no claim)")
        elif result["verdict"] == "defect":
            print("❌ DEFECT DETECTED")


if __name__ == "__main__":
    main()
