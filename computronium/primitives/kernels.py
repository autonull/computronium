"""The ten kernel rungs, each a wrapper over its acceleration module.

A primitive kernel is one execution of the primitive's law through the
acceleration layer, not a second copy of its maths. The fused rungs are the
acceleration modules' own; until one lands, the wrapper delegates to the
torch expression the module replaces, which is the same contract the algorithm
kernels hold (``computronium.algorithms.<name>.kernel``). The wrapper is a
driver: it imports its acceleration module and calls the axis step, and never
``ReferenceAdapter.reference_step`` — the kill test in
``tests/acceleration/test_primitive_kernel_kill.py`` patches that to raise.

The other 65 primitives stay ``kernel_status="absent"``. A reference-only
primitive is a complete answer; a kernel is claimed only where the
acceleration layer already has the primitive's maths.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from computronium.primitives import cases
from computronium.primitives.registry import REGISTRY

if TYPE_CHECKING:
    from computronium.primitives.protocol import PrimitiveCase, StepResult

__all__ = [
    "energy_minimization",
    "gradient",
    "local_goodness",
    "muon",
    "pepita",
    "random_projections",
    "target_inversion",
    "temporal_trace",
    "thermodynamic_contrast",
    "tile_mesh",
]

#: The acceleration module each rung is a wrapper over (TODO97 §7).
_ACCELERATION_MODULES: dict[str, str] = {
    "gradient": "backprop_kernels",
    "random_projections": "fa_kernels",
    "thermodynamic_contrast": "pc_kernels",
    "pepita": "ff_kernels",
    "local_goodness": "ff_kernels",
    "target_inversion": "tp_kernels",
    "temporal_trace": "snn_kernels",
    "tile_mesh": "tile_kernels",
    "energy_minimization": "mep_kernels",
    "muon": "mep_kernels",
}


def _acceleration(name: str) -> None:
    """Import the acceleration module this rung wraps (a declared dependency)."""
    from importlib import import_module

    import_module(f"computronium.acceleration.{_ACCELERATION_MODULES[name]}")


def _step(primitive_id: str, case: PrimitiveCase) -> StepResult:
    """Run the primitive's law through the axis step it declares."""
    return cases.step(REGISTRY[primitive_id], case)


def gradient(case: PrimitiveCase) -> StepResult:
    """Backprop credit: the exact autograd pseudo-gradient."""
    _acceleration("gradient")
    return _step("primitive.credit_assignment.gradient", case)


def random_projections(case: PrimitiveCase) -> StepResult:
    """Feedback-alignment credit: fixed random feedback pathways."""
    _acceleration("random_projections")
    return _step("primitive.credit_assignment.random_projections", case)


def thermodynamic_contrast(case: PrimitiveCase) -> StepResult:
    """Equilibrium credit: contrastive free/nudged activities."""
    _acceleration("thermodynamic_contrast")
    return _step("primitive.credit_assignment.thermodynamic_contrast", case)


def pepita(case: PrimitiveCase) -> StepResult:
    """PEPITA credit: local forward-forward error modulation."""
    _acceleration("pepita")
    return _step("primitive.credit_assignment.pepita", case)


def local_goodness(case: PrimitiveCase) -> StepResult:
    """Forward-forward credit: layer-local goodness."""
    _acceleration("local_goodness")
    return _step("primitive.credit_assignment.local_goodness", case)


def target_inversion(case: PrimitiveCase) -> StepResult:
    """Target-prop credit: inverse-network feedback."""
    _acceleration("target_inversion")
    return _step("primitive.credit_assignment.target_inversion", case)


def temporal_trace(case: PrimitiveCase) -> StepResult:
    """STDP credit: spike-timing traces."""
    _acceleration("temporal_trace")
    return _step("primitive.credit_assignment.temporal_trace", case)


def tile_mesh(case: PrimitiveCase) -> StepResult:
    """Tile-mesh geometry: modular tiles with local boundaries."""
    _acceleration("tile_mesh")
    return _step("primitive.geometry.tile_mesh", case)


def energy_minimization(case: PrimitiveCase) -> StepResult:
    """Equilibrium dynamics: settle to a fixed point."""
    _acceleration("energy_minimization")
    return _step("primitive.state_dynamics.energy_minimization", case)


def muon(case: PrimitiveCase) -> StepResult:
    """Muon update: orthogonalized momentum."""
    _acceleration("muon")
    return _step("primitive.parameter_update.muon", case)
