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
from pathlib import Path
from typing import Annotated, Any, Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from computronium.experiment.schema.axis import AXES_REGISTRIES, Domain, StructuralAxis

RUN_SPEC_VERSION = 2

Fidelity = Literal["L0", "L1", "L2"]

_NONNEG = Annotated[int, Field(ge=0)]
_POSITIVE = Annotated[int, Field(gt=0)]


class AxisSelection(BaseModel):
    """A run's restriction of one structural axis, and its searched domains.

    ``primitives=None`` means every available primitive on the axis.  ``domains``
    narrows a hyperparameter's harvested domain for this run; an empty mapping
    keeps the harvested one.  Names are validated against ``AXES_REGISTRIES``
    and the harvested schema, so a typo fails the run rather than silently
    narrowing the space to nothing.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    axis: StructuralAxis
    primitives: tuple[str, ...] | None = None
    domains: dict[str, Domain] = Field(default_factory=dict)

    @model_validator(mode="after")
    def _known_names(self) -> Self:
        from computronium.experiment.schema.harvest import harvest_schema

        registry = AXES_REGISTRIES[self.axis]
        if self.primitives is not None:
            unknown = [p for p in self.primitives if p not in registry]
            if unknown:
                msg = (
                    f"axes[{self.axis}].primitives names unknown primitive(s) "
                    f"{unknown}; available: {sorted(registry.keys())}"
                )
                raise ValueError(msg)
        available = harvest_schema().by_name()
        unknown = [d for d in self.domains if d not in available]
        if unknown:
            msg = (
                f"axes[{self.axis}].domains names unknown hyperparameter(s) "
                f"{unknown}; harvested: {sorted(available)}"
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


class RunSpec(BaseModel):
    """The complete, validated declaration of one run.

    Versioned, diffable, and reproducible: a run's records are only as
    reproducible as this object, so it names its task, objectives, stage
    sequence, fidelity, seed plan, budget, policy, and the axis subsets and
    hyperparameter domains to search (``axes=()`` means the whole registry).
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
    policy: str | None = None
    axes: tuple[AxisSelection, ...] = ()
    operating_points: dict[str, Any] = Field(default_factory=dict)
    dataset: str = "unknown"
    dataset_version: str = "1.0"
    code_sha: str = "unknown"

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
        if self.stages is not None:
            known = tuple(s.value for s in StageId)
            unknown = [s for s in self.stages if s not in known]
            if unknown:
                msg = f"unknown stage(s) {unknown}; available: {list(known)}"
                raise ValueError(msg)
        if self.policy is not None and self.policy not in POLICY_CATALOG:
            msg = f"unknown policy {self.policy!r}; available: {sorted(POLICY_CATALOG)}"
            raise ValueError(msg)
        duplicated = sorted({
            s.axis for s in self.axes if [x.axis for x in self.axes].count(s.axis) > 1
        })
        if duplicated:
            msg = f"axes names the same axis more than once: {duplicated}"
            raise ValueError(msg)
        return self

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

        Raises:
            ValueError: the file is not JSON, or names an unknown field, an
                unresolvable task, objective, stage or policy.
        """
        raw = Path(path).read_text(encoding="utf-8")
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            msg = f"{path} is not valid JSON: {exc}"
            raise ValueError(msg) from exc
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


__all__ = ["RUN_SPEC_VERSION", "AxisSelection", "Fidelity", "RunSpec"]
