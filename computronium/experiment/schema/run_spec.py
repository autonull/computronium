"""Typed ``RunSpec``: the one declaration of what a run searches.

A run spec is the only description of a run that survives it: it is what the
CLI loads, what ``runs.spec`` persists, and what ``PipelineConfig`` reads.  It
is validated once, at the boundary (TODO46 D4/§3.2), so every reader downstream
consumes a checked object instead of a dict whose keys are an implicit
contract spread across six modules.

Field names are canonical.  Historical spellings (``seeds`` for a *count* of
seeds, ``operating_point`` singular, ``n_seeds``) are gone; a spec that used
one now fails validation naming the field rather than being silently ignored.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Annotated, Any, Final, Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from computronium.experiment.schema.axis import (
    AXES_REGISTRIES,
    Domain,
    Scale,
    StructuralAxis,
)
from computronium.experiment.schema.harvest import harvest_schema
from computronium.experiment.schema.metrics import MEASURED_OBJECTIVES
from computronium.experiment.schema.registries import validate_rate_value

logger = logging.getLogger(__name__)

RUN_SPEC_VERSION = 2

# The ceiling the digits campaign measured (TODO46 §8 session 6). Sized to the
# unconstrained default (a 64x2 feedforward is 8 970 parameters) so a bounded
# run is not *slower* than an unbounded one, while cutting the cells that cost:
# unconstrained, a lattice cell composes at 839 690 parameters and dominates the
# suite. Every topology the kernel can train composes under 10 000 and trains
# four batches in under 0.5 s; ``test_param_budget_lock.py`` holds both claims.
MEASURED_PARAM_BUDGET: Final[int] = 10_000

# Broader parameter budget for multi-substrate profiles (production-map,
# maturation, claim). The 9-substrate space with hidden_dim sweep (8-526)
# exceeds 10k for most non-digital substrates. 50k allows all substrates to
# participate while still providing a meaningful constraint.
BROAD_PARAM_BUDGET: Final[int] = 50_000

# The rest of the measured regime (TODO46 §6.1): what a cell actually costs. Two
# batches on digits is a real forward/backward pass and a real gradient step, so
# the acceptance gate locks orchestration and measurement identity without paying
# for 45 batches it does not need; the full-regime evidence lives in one
# demo-marked test (tests/acceptance/test_demo_acceptance_full_regime.py).
# Unbounded training and validation made the gate cost 12 minutes, and every
# unbound number is eventually charged to the wall clock instead of the run.
MEASURED_BATCH_LIMIT: Final[int] = 2

Fidelity = Literal["L0", "L1", "L2"]

_NONNEG = Annotated[int, Field(ge=0)]
_POSITIVE = Annotated[int, Field(gt=0)]


class AxisSelection(BaseModel):
    """A run's restriction of one structural axis.

    ``primitives=None`` means every available primitive on the axis.  Names are
    validated against ``AXES_REGISTRIES``, so a typo fails the run rather than
    silently narrowing the space to nothing.

    Hyperparameter domains are *not* declared here: a hyperparameter is read by
    whichever primitive needs it, so its domain belongs to the run
    (``RunSpec.hyperparameters``), not to an axis that would be an arbitrary
    choice of owner. Names are per-axis (``settle_step``, ``update_lr``); the
    schema seam lock rejects any name claimed by two axes.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    axis: StructuralAxis
    primitives: tuple[str, ...] | None = None

    @model_validator(mode="after")
    def _known_names(self) -> Self:
        registry = AXES_REGISTRIES[self.axis]
        if self.primitives is not None:
            unknown = [p for p in self.primitives if p not in registry]
            if unknown:
                msg = (
                    f"axes[{self.axis}].primitives names unknown primitive(s) "
                    f"{unknown}; available: {sorted(registry.keys())}"
                )
                raise ValueError(msg)
        return self

    def selected(self) -> tuple[str, ...]:
        """The primitive names this selection permits."""
        if self.primitives is not None:
            return self.primitives
        return tuple(
            sorted(n for n, s in AXES_REGISTRIES[self.axis].items() if s.available)
        )


def _check_axes_distinct(axes: tuple[AxisSelection, ...]) -> None:
    """No axis may be declared twice: its selection would be ambiguous.

    Args:
        axes: The spec's axis selections.

    Raises:
        ValueError: If any axis appears more than once.
    """
    names = [a.axis for a in axes]
    duplicated = sorted({n for n in names if names.count(n) > 1})
    if duplicated:
        msg = f"axes names the same axis more than once: {duplicated}"
        raise ValueError(msg)


def _check_declared_rates(hyperparameters: dict[str, Domain]) -> None:
    """Every declared bound of a rate parameter must be positive.

    ``update_lr: {lo: 0}`` is not a small sweep, it is a sweep that trains
    nothing and reports a plausible number. Rejected at the declaration,
    beside the other declaration errors, rather than diagnosed after training.

    Args:
        hyperparameters: The spec's swept hyperparameters, by name.

    Raises:
        ValueError: If a rate parameter declares a non-positive bound.
    """
    for name, domain in hyperparameters.items():
        for bound in (domain.lo, domain.hi):
            if bound is not None:
                validate_rate_value(name, bound)


class RunSpec(BaseModel):
    """The complete, validated declaration of one run.

    Versioned, diffable, and reproducible: a run's records are only as
    reproducible as this object, so it names its task, objectives, stage
    sequence, fidelity, seed plan, budget, policy, and the axis subsets and
    hyperparameter domains to search (``axes=()`` means the whole registry), and
    the parameter ceiling its cells are sized under.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    version: int = RUN_SPEC_VERSION
    profile: str = "custom"
    task: str | None = None
    tasks: tuple[str, ...] = ()
    objectives: tuple[str, ...] = ()
    stages: tuple[str, ...] | None = None
    fidelity: Fidelity = "L0"
    n_seeds: _POSITIVE = 1
    epochs: _POSITIVE = 1
    batch_limit: _NONNEG = 0
    seed: _NONNEG = 0
    budget_seconds: Annotated[float, Field(gt=0)] | None = None
    # A parameter ceiling for derived geometry sizing; 0 is unconstrained. It
    # travels on the Schedule, because it changes what is trained.
    param_budget: _NONNEG = 0
    policy: str | None = None
    axes: tuple[AxisSelection, ...] = ()
    hyperparameters: dict[str, Domain] = Field(default_factory=dict)
    operating_points: dict[str, Any] = Field(default_factory=dict)
    dataset: str = "unknown"
    dataset_version: str = "1.0"
    code_sha: str = "unknown"
    device: str = "auto"
    # Use deterministic algorithms (sets torch.use_deterministic_algorithms)
    deterministic: bool = False
    # DataLoader num_workers (0 for single-threaded determinism)
    num_workers: int = 0
    # Axis-aligned objective sets: mapping from axis name to tuple of objective names.
    # When set, the policy will use per-axis objective sets for multi-objective optimization.
    # Format: {"substrate": ("energy_efficiency", "latency_ms", "precision"), ...}
    axis_objectives: dict[str, tuple[str, ...]] = Field(default_factory=dict)
    # Hyperparameter sweep steps: number of diagonal steps through the hyperparameter space.
    # Default 5; increase for finer coverage (e.g., 50 for factorial-like sweep).
    sweep_steps: _POSITIVE = 5

    @model_validator(mode="after")
    def _check(self) -> Self:
        from computronium.domains.registry import SUPPORTED_TASKS
        from computronium.experiment.execution.policy import POLICY_CATALOG
        from computronium.experiment.execution.stage import StageId
        from computronium.experiment.schema.registries import OBJECTIVES_REGISTRY

        if not self.task_names:
            msg = f"run names no task; known: {sorted(SUPPORTED_TASKS)}"
            raise ValueError(msg)
        unknown = [t for t in self.task_names if t not in SUPPORTED_TASKS]
        if unknown:
            msg = f"unknown task(s) {unknown}; available: {sorted(SUPPORTED_TASKS)}"
            raise ValueError(msg)
        unknown = [o for o in self.objectives if o not in OBJECTIVES_REGISTRY]
        if unknown:
            msg = (
                f"unknown objective(s) {unknown}; "
                f"available: {sorted(OBJECTIVES_REGISTRY.keys())}"
            )
            raise ValueError(msg)

        # Reject unmeasured objectives in the main objectives list.
        # They can only appear in axis_objectives (for documentation/planning).
        # A run that declares an objective it cannot measure makes a claim it withdraws silently.
        unmeasured = [
            o for o in self.objectives if OBJECTIVES_REGISTRY[o].metric_key is None
        ]
        if unmeasured:
            msg = (
                f"objective(s) {unmeasured} have no measurement (metric_key is None); "
                f"they cannot be used in the main objectives list. "
                f"Measured objectives: {sorted(MEASURED_OBJECTIVES.keys())}"
            )
            raise ValueError(msg)
        if self.stages is not None:
            known = tuple(s.value for s in StageId)
            unknown = [s for s in self.stages if s not in known]
            if unknown:
                msg = f"unknown stage(s) {unknown}; available: {list(known)}"
                raise ValueError(msg)
        if self.policy is not None and self.policy not in POLICY_CATALOG:
            msg = f"unknown policy {self.policy!r}; available: {sorted(POLICY_CATALOG)}"
            raise ValueError(msg)
        if self.device not in {"cpu", "cuda", "auto"}:
            msg = f"invalid device {self.device!r}; expected 'cpu', 'cuda', or 'auto'"
            raise ValueError(msg)
        if self.num_workers < 0:
            msg = f"num_workers must be non-negative, got {self.num_workers}"
            raise ValueError(msg)

        # Validate axis_objectives
        from computronium.experiment.schema.registries import (
            OBJECTIVES_REGISTRY as OBJ_REG,
        )

        axis_tags = sorted({
            spec.axis_tag for spec in OBJ_REG.values() if spec.axis_tag is not None
        })
        for axis_name, obj_names in self.axis_objectives.items():
            for obj_name in obj_names:
                if obj_name not in OBJ_REG:
                    msg = (
                        f"axis_objectives[{axis_name!r}] names unknown objective {obj_name!r}; "
                        f"available: {sorted(OBJ_REG.keys())}"
                    )
                    raise ValueError(msg)
            # Ensure axis name is a valid axis tag from objectives registry
            if axis_name not in axis_tags:
                msg = (
                    f"axis_objectives names unknown axis tag {axis_name!r}; "
                    f"available: {axis_tags}"
                )
                raise ValueError(msg)

        harvested = harvest_schema().by_name()
        unknown = [h for h in self.hyperparameters if h not in harvested]
        if unknown:
            msg = (
                f"hyperparameters names unknown name(s) {unknown}; "
                f"harvested: {sorted(harvested)}"
            )
            raise ValueError(msg)
        _check_declared_rates(self.hyperparameters)
        structural = sorted(
            h
            for h, spec in harvested.items()
            if self.hyperparameters.get(h) is not None
            and spec.axis_kind.value == "structural"
        )
        if structural:
            msg = (
                f"hyperparameter(s) {structural} are structural — derived from the "
                "task or chosen by the run — and cannot be swept"
            )
            raise ValueError(msg)

        # Auto-narrow hidden_dim domain based on param_budget
        if (
            self.param_budget > 0
            and "hidden_dim" not in self.hyperparameters
            and self.task_names
        ):
            from computronium.experiment.execution.evaluate import task_shape

            try:
                task_shape_obj = task_shape(self.task_names[0])
                max_h = self._max_hidden_dim_for_budget(
                    self.param_budget,
                    task_shape_obj.input_shape[-1],
                    task_shape_obj.output_dim,
                )
                # Create a new dict with the narrowed domain
                narrowed_hyperparameters = dict(self.hyperparameters)
                narrowed_hyperparameters["hidden_dim"] = Domain(
                    lo=8, hi=max_h, scale=Scale.LOG
                )
                object.__setattr__(self, "hyperparameters", narrowed_hyperparameters)
            except (
                Exception
            ):  # pragma: no cover - task shape may not be resolvable at validation time
                # If task shape resolution fails, skip auto-narrowing
                logger.debug(
                    "Auto-narrowing hidden_dim failed, skipping", exc_info=True
                )

        _check_axes_distinct(self.axes)
        return self

    @staticmethod
    def _max_hidden_dim_for_budget(
        param_budget: int, input_dim: int, output_dim: int
    ) -> int:
        """Estimate maximum hidden_dim that fits within param_budget for a single layer."""
        if param_budget <= 0:
            return 4096
        denom = input_dim + output_dim + 1
        return max(8, min(4096, param_budget // max(1, denom)))

    @property
    def task_names(self) -> tuple[str, ...]:
        """Every task this run measures, singular field first."""
        return tuple(dict.fromkeys(n for n in (self.task, *self.tasks) if n))

    @property
    def stage_names(self) -> tuple[str, ...]:
        """The stage sequence; ``None`` means the canonical S1-S11 order."""
        if self.stages is not None:
            return self.stages
        from computronium.experiment.execution.stage import StageId

        return tuple(s.value for s in StageId)

    def selection(self, axis: StructuralAxis) -> AxisSelection | None:
        """The run's restriction of ``axis``, or ``None`` for unrestricted."""
        for sel in self.axes:
            if sel.axis == axis:
                return sel
        return None

    def selected_primitives(self, axis: StructuralAxis) -> tuple[str, ...]:
        """Every primitive the run permits on ``axis``."""
        sel = self.selection(axis)
        if sel is not None:
            return sel.selected()
        return tuple(sorted(n for n, s in AXES_REGISTRIES[axis].items() if s.available))

    def to_dict(self) -> dict[str, Any]:
        """The JSON-ready mapping persisted in ``runs.spec``."""
        return self.model_dump(mode="json")

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        """Validate a mapping into a spec."""
        return cls.model_validate(data)

    @classmethod
    def load(cls, path: str | Path) -> Self:
        """Validate a spec file.

        The format follows the suffix — ``.yaml``/``.yml`` are YAML, ``.json``
        is JSON — so a spec written by hand and a spec emitted by
        ``to_dict`` load through one declaration and neither is guessed at.

        Raises:
            ValueError: the suffix names no known format, the file does not
                parse, or it names an unknown field, an unresolvable task,
                objective, stage or policy.
        """
        spec_path = Path(path)
        raw = spec_path.read_text(encoding="utf-8")
        suffix = spec_path.suffix.lower()
        if suffix in {".yaml", ".yml"}:
            import yaml

            try:
                data = yaml.safe_load(raw)
            except yaml.YAMLError as exc:
                msg = f"{spec_path} is not valid YAML: {exc}"
                raise ValueError(msg) from exc
        elif suffix == ".json":
            try:
                data = json.loads(raw)
            except json.JSONDecodeError as exc:
                msg = f"{spec_path} is not valid JSON: {exc}"
                raise ValueError(msg) from exc
        else:
            msg = (
                f"{spec_path}: unknown spec format {suffix!r}; use .json, .yaml or .yml"
            )
            raise ValueError(msg)
        return cls.model_validate(data)

    def diff(self, other: RunSpec) -> dict[str, tuple[Any, Any]]:
        """Fields whose values differ from ``other``, as ``(mine, theirs)``.

        The R41 diff gate: two specs are comparable field-wise, so a change is
        nameable rather than a whole-document judgment.
        """
        mine, theirs = self.to_dict(), other.to_dict()
        return {
            k: (mine[k], theirs[k])
            for k in sorted(mine.keys() | theirs.keys())
            if mine.get(k) != theirs.get(k)
        }


__all__ = [
    "BROAD_PARAM_BUDGET",
    "MEASURED_BATCH_LIMIT",
    "MEASURED_PARAM_BUDGET",
    "RUN_SPEC_VERSION",
    "AxisSelection",
    "Fidelity",
    "RunSpec",
]
