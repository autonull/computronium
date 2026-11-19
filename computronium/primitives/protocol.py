"""Primitive Protocol — Single-source specification and execution interface.

This module defines the core types for the primitive layer migration (TODO97).
Replaces ~380 per-primitive spec/cases/reference/kernel files with a single
registry of 75 PrimitiveSpec rows and a generic ReferenceAdapter.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal, Protocol, runtime_checkable

import torch
from torch import Tensor


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
    kernel_technology: Literal["torch", "triton", "cuda", "torch_compile", "cupy", "numpy"] | None = None
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


# Generic adapter that calls the ontology class's declared entrypoint
class ReferenceAdapter:
    """Generic reference adapter — no per-primitive code needed.

    The SPEC.config_factory points to a config classmethod (e.g.
    CreditAssignmentConfig.random_projections). The ontology class is
    instantiated with that config, and its entrypoint method is called.
    """

    SPEC: PrimitiveSpec

    def __init__(self, spec: PrimitiveSpec):
        self.SPEC = spec

    def make_task_case(self, task_id: str, box: dict, seed: int) -> Any:
        """Create a test case using TaskRegistry + the spec's config factory."""
        from computronium.experiment.task_registry import TaskRegistry
        from importlib import import_module

        task = TaskRegistry.get(task_id)
        config_factory = self._import_callable(self.SPEC.config_factory)
        config = config_factory()

        # Task-specific case creation (delegates to task)
        return task.make_case(config=config, box=box, seed=seed)

    def reference_step(self, case: Any) -> StepResult:
        """Call the ontology class's reference entrypoint."""
        from importlib import import_module

        entrypoint = self._import_callable(self.SPEC.reference_entrypoint)
        result = entrypoint(case)

        # Normalize to StepResult
        if isinstance(result, StepResult):
            return result
        if isinstance(result, list):
            # Assume list of weight gradients
            return StepResult(
                weights=result,
                activations=getattr(case, "activations", []),
                metrics={},
                state={},
            )
        raise TypeError(f"Reference entrypoint returned {type(result)}, expected StepResult or list[Tensor]")

    def kernel_step(self, case: Any) -> StepResult:
        """Call the kernel entrypoint or raise if absent."""
        if self.SPEC.kernel_status == "absent":
            raise RuntimeError(f"Kernel not implemented for {self.SPEC.id}")
        if self.SPEC.kernel_status == "stub":
            # For parity tests only — returns reference
            return self.reference_step(case)
        if self.SPEC.kernel_entrypoint is None:
            raise RuntimeError(f"Kernel entrypoint not set for {self.SPEC.id}")

        from importlib import import_module

        entrypoint = self._import_callable(self.SPEC.kernel_entrypoint)
        result = entrypoint(case)

        if isinstance(result, StepResult):
            return result
        if isinstance(result, list):
            return StepResult(
                weights=result,
                activations=getattr(case, "activations", []),
                metrics={},
                state={},
            )
        raise TypeError(f"Kernel entrypoint returned {type(result)}, expected StepResult or list[Tensor]")

    def fingerprint(self, case: Any) -> str:
        """Compute a deterministic fingerprint from the case output."""
        result = self.reference_step(case)
        import hashlib

        # Hash the weights
        hasher = hashlib.blake2b(digest_size=16)
        for w in result.weights:
            hasher.update(w.detach().cpu().numpy().tobytes())
        return hasher.hexdigest()

    def analytic_invariant(self, case: Any) -> bool:
        """Check the axis-level analytic invariant.

        Delegates to the axis-specific invariant function.
        """
        axis = self.SPEC.axis
        if axis == "credit":
            from computronium.experiment.invariants import credit_invariant
            return credit_invariant(case, self)
        elif axis == "dynamics":
            from computronium.experiment.invariants import dynamics_invariant
            return dynamics_invariant(case, self)
        elif axis == "geometry":
            from computronium.experiment.invariants import geometry_invariant
            return geometry_invariant(case, self)
        elif axis == "plasticity":
            from computronium.experiment.invariants import plasticity_invariant
            return plasticity_invariant(case, self)
        elif axis == "substrate":
            from computronium.experiment.invariants import substrate_invariant
            return substrate_invariant(case, self)
        elif axis == "update":
            from computronium.experiment.invariants import update_invariant
            return update_invariant(case, self)
        return False

    def _import_callable(self, dotted_path: str):
        """Import a callable from a dotted path."""
        from importlib import import_module

        module_path, func_name = dotted_path.rsplit(".", 1)
        module = import_module(module_path)
        return getattr(module, func_name)