"""Primitive Protocol — Single-source specification and execution interface.

This module defines the core types for the primitive layer migration (TODO97).
Replaces ~380 per-primitive spec/cases/reference/kernel files with a single
registry of 75 PrimitiveSpec rows and a generic ReferenceAdapter.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Literal, Protocol, runtime_checkable

if TYPE_CHECKING:
    from torch import Tensor


@dataclass(frozen=True, slots=True)
class PrimitiveCase:
    """Universal test case for any primitive.

    Replaces per-primitive case classes. The config is the primitive's
    config object; the box is the hyperparameter box; the seed ensures
    determinism. Task-specific data (batch, targets) is populated lazily
    by the experiment harness.
    """

    config: Any
    box: dict[str, Any]
    seed: int
    task_id: str
    # Task-specific data (populated by experiment harness)
    batch: tuple[Tensor, Tensor] | None = None
    # Extra fields for axis-specific needs
    extra: dict[str, Any] = field(default_factory=dict)

    # The harness's payload view: the case builders store these under ``extra``,
    # and the shared harness helpers (e.g. ``update_geometry``) read them by name.
    @property
    def state(self) -> Any:
        """The case's input state."""
        return self.extra.get("state")

    @property
    def prediction(self) -> Any:
        """The case's readout the update acts on."""
        return self.extra.get("prediction")

    @property
    def multiplier(self) -> Any:
        """The case's per-example weight of the readout."""
        return self.extra.get("multiplier")


@dataclass(frozen=True, slots=True)
class StepResult:
    """Result of a primitive step (reference or kernel)."""

    weights: list[Tensor]
    activations: list[Tensor]
    metrics: dict[str, float]
    state: dict[str, Any]


@dataclass(frozen=True, slots=True)
class PrimitiveSpec:
    """Complete specification for a primitive.

    One row per primitive — replaces the per-primitive spec.py files.
    """

    id: str
    axis: Literal["credit", "dynamics", "geometry", "plasticity", "substrate", "update"]
    name: str
    equations: str
    invariants: tuple[str, ...]
    task_families: tuple[str, ...]
    ontology_class: type
    config_factory: str  # Dotted path to config classmethod, e.g. "CreditAssignmentConfig.random_projections"
    reference_entrypoint: str  # Dotted path to reference function
    kernel_status: Literal["implemented", "wrapper", "stub", "absent"] = "absent"
    kernel_entrypoint: str | None = None
    kernel_technology: (
        Literal["torch", "triton", "cuda", "torch_compile", "cupy", "numpy"] | None
    ) = None
    supported_backends: tuple[Literal["reference", "kernel"], ...] = ("reference",)
    available: bool = True
    capability_card: str = ""
    summary: str = ""
    invariants_notes: str = ""
    tags: tuple[str, ...] = ()


@runtime_checkable
class PrimitiveProtocol(Protocol):
    """Protocol that all primitives implement.

    The registry holds PrimitiveSpec rows; this protocol defines the
    operations the experiment harness can invoke.
    """

    SPEC: PrimitiveSpec

    def make_task_case(self, task_id: str, box: dict, seed: int) -> Any:
        """Create a deterministic test case for the given task and box."""

    def reference_step(self, case: Any) -> StepResult:
        """Execute the reference implementation step."""

    def kernel_step(self, case: Any) -> StepResult:
        """Execute the accelerated kernel step (raises if kernel_status == "absent")."""

    def fingerprint(self, case: Any) -> str:
        """Compute a deterministic fingerprint of the case output."""

    def analytic_invariant(self, case: Any) -> bool:
        """Check the axis-level analytic invariant for this primitive."""


class ReferenceAdapter:
    """The one adapter every primitive spec runs through.

    ``make_task_case`` builds the axis's micro-case from the composed typed
    config; ``reference_step`` runs the spec's law on it. The per-primitive
    difference is data (``PrimitiveSpec``), so a new primitive is a registry row
    and never a new adapter.
    """

    SPEC: PrimitiveSpec

    def __init__(self, spec: PrimitiveSpec):
        self.SPEC = spec

    def make_task_case(
        self, task_id: str = "mnist", box: dict | None = None, seed: int = 0
    ) -> PrimitiveCase:
        """Build the deterministic case the spec's reference step consumes."""
        from computronium.primitives import cases

        return cases.build_case(self.SPEC, task_id, box, seed)

    def reference_step(self, case: Any) -> StepResult:
        """Run the spec's law on ``case``."""
        from computronium.primitives import cases

        return cases.step(self.SPEC, case)

    def kernel_step(self, case: Any) -> StepResult:
        """Call the kernel entrypoint, or raise when the kernel is absent."""
        if self.SPEC.kernel_status == "absent":
            msg = f"Kernel not implemented for {self.SPEC.id}"
            raise RuntimeError(msg)
        if self.SPEC.kernel_entrypoint is None:
            msg = f"Kernel entrypoint not set for {self.SPEC.id}"
            raise RuntimeError(msg)
        return _resolve_step(self.SPEC.kernel_entrypoint, case)

    def fingerprint(self, case: Any) -> str:
        """A deterministic digest of the spec's step output."""
        from computronium.acceleration.parity import digest

        return digest(self.reference_step(case))

    def analytic_invariant(self, case: Any) -> bool:
        """Whether the spec's axis-level invariant holds on ``case``."""
        from computronium.primitives import cases

        return cases.invariant(self.SPEC, case)


def _resolve_step(dotted_path: str, case: Any) -> StepResult:
    """Run a kernel entrypoint named by ``dotted_path`` on ``case``."""
    from importlib import import_module

    module_path, _, attribute = dotted_path.rpartition(".")
    module = import_module(module_path)
    entrypoint = getattr(module, attribute, None)
    if entrypoint is None:
        msg = f"Could not import {dotted_path}"
        raise ImportError(msg)
    result = entrypoint(case)
    if isinstance(result, StepResult):
        return result
    if isinstance(result, list):
        return StepResult(weights=result, activations=[], metrics={}, state={})
    msg = f"Kernel entrypoint returned {type(result)}, expected StepResult"
    raise TypeError(msg)


#: The reference entrypoint every spec on an axis shares.
_AXIS_REFERENCE_ENTRYPOINTS: dict[str, str] = {
    "credit": "computronium.primitives.cases.step",
    "dynamics": "computronium.primitives.cases.step",
    "geometry": "computronium.primitives.cases.step",
    "plasticity": "computronium.primitives.cases.step",
    "substrate": "computronium.primitives.cases.step",
    "update": "computronium.primitives.cases.step",
}
