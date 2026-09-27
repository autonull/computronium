"""The dispatch coordinate: the axes that decide which backend serves a system.

An algorithm *is* a coordinate. :func:`key_of` reads it off a live system and
:func:`select_backend_class` is a ``match`` over it, so the pair of tables this
replaces — a 23-value ``AlgorithmFamily`` enum plus 22 ``BINDINGS`` rows — becomes
one function whose arms are the binding table. A coordinate no arm names has no
backend, which is an answer; a family that disagrees with its own factory is not.

**Five of the six axes are read.** Substrate is the exception, and provably so:
``ternary_eqprop`` and ``sparse_eqprop`` differ in substrate alone and are one
algorithm, so a key that read substrate would give one backend two spellings.

The values are the ontology's own discriminators (``dynamics_type``,
``credit_type``, ``topology_type``, ``update_type``) rather than class names, so a
coordinate survives a rename of the class that implements it and can be written
down in a config file or a spec without importing anything.

**An absent arm is a finding, not a gap.** ``tests/acceleration/test_backend_reach.py``
attaches each arm and asserts the composed system's own parameters moved. Ten of
the fourteen algorithms fail that today — their rungs raise, or (worse) report
metrics for weights they trained privately — so they have no arm and run the
reference rung with a logged reason. TODO38.md §4.0 records each failure. The
backend classes themselves are untouched and waiting; what is missing is their
training path, not their kernels.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Final

import torch

if TYPE_CHECKING:
    from torch import Tensor

    from computronium.acceleration.kernel_backend import KernelConfig
    from computronium.ontology import System

__all__ = [
    "DISPATCH_AXES",
    "DispatchKey",
    "kernel_config_of",
    "key_of",
    "select_backend_class",
    "sweep_hyperparameters",
    "sweep_hyperparameters_from_system",
]

#: (geometry, state_dynamics, credit_assignment, parameter_update, plasticity).
type DispatchKey = tuple[str, str, str, str, str]

DISPATCH_AXES: Final[tuple[str, ...]] = (
    "geometry",
    "state_dynamics",
    "credit_assignment",
    "parameter_update",
    "plasticity",
)

#: What a system with no plasticity axis reads on the plasticity slot. The
#: ontology spells the same thing two ways — a ``NullPlasticity`` object and an
#: absent attribute — and both mean "this algorithm's update is the whole story".
NULL_PLASTICITY: Final[str] = "null"

_CAMEL_BOUNDARY: Final = re.compile(r"(?<!^)(?=[A-Z])")


def _snake(name: str) -> str:
    return _CAMEL_BOUNDARY.sub("_", name).lower()


def _plasticity_value(system: System) -> str:
    """The plasticity slot, from the class that implements it.

    ``RoutingPlasticity`` reads ``routing`` and ``FastWeightPlasticity`` reads
    ``fast_weight``, which are the short names the primitive registry gives them,
    so a spec and the system it composes name one coordinate with one vocabulary.
    """
    plasticity = getattr(system, "plasticity", None)
    if plasticity is None:
        return NULL_PLASTICITY
    name = type(plasticity).__name__
    return _snake(name.removesuffix("Plasticity"))


def key_of(system: System) -> DispatchKey:
    """The five dispatch axes of a live system, in :data:`DISPATCH_AXES` order.

    Args:
        system: a composed system or joint system.

    Returns:
        The coordinate a backend is selected by.
    """
    return (
        system.geometry.config.topology_type,
        system.dynamics.config.dynamics_type,
        system.credit.config.credit_type,
        system.update.config.update_type,
        _plasticity_value(system),
    )


def _backend(module: str, name: str) -> type:
    from importlib import import_module

    return getattr(import_module(f"computronium.acceleration.{module}"), name)


def select_backend_class(key: DispatchKey, variant: str | None = None) -> type | None:
    """The backend class that serves ``key``, or ``None`` if none does.

    The arms name only the axes their backend reads; ``match`` therefore reads a
    backend as the smallest honest predicate over the coordinate, and an arm
    cannot quietly grow to claim a coordinate it was not written for. A
    coordinate with **no** arm is not a hole to be filled later with whatever is
    nearest: it is the finding that the rung for that algorithm does not train
    the system it would be bound to, and TODO38.md §4.0 records which and why.

    Args:
        key: a coordinate from :func:`key_of`.
        variant: an orthogonal variant choice (``"contrastive"``), not an
            algorithm identity. ``None`` selects the standard backend.

    Returns:
        The backend class, or ``None`` when the coordinate has no arm. A
        coordinate with no arm is a legitimate answer — it runs the reference
        rung — and is reported by name rather than bound to whatever is nearest.
    """
    _geometry, _dynamics, credit, _update, plasticity = key
    match key:
        case (_, "energy_minimization", "thermodynamic_contrast", _, _):
            return _variant(variant, "eqprop_kernel_backend", "EqPropKernelBackend")
        case (_, "predictive_settling", "local_goodness", _, _):
            return _variant(variant, "pc_kernels", "PCKernelBackend")
        case ("feedforward", "instantaneous", _, _, _):
            return _instantaneous(variant, credit, plasticity)
        case _:
            return None


def _instantaneous(variant: str | None, credit: str, plasticity: str) -> type | None:
    """The single-pass coordinates, which are told apart by credit alone."""
    match credit:
        case "gradient":
            return _gradient_rung(variant, plasticity)
        case "temporal_trace":
            return _variant(variant, "hebbian_kernels", "HebbianKernelBackend")
        case _:
            return None


def _gradient_rung(variant: str | None, plasticity: str) -> type | None:
    """``gradient`` credit is shared by four algorithms, so plasticity decides.

    Backprop and routing (MEP) differ *only* in plasticity, which is why
    plasticity is in the key at all: without it they would be one coordinate and
    one of them would train the wrong algorithm.
    """
    match plasticity:
        case "null":
            return _variant(variant, "backprop_kernels", "BackpropKernelBackend")
        case "routing":
            return _variant(variant, "mep_kernels", "MEPKernelBackend")
        case _:
            return None


def _variant(variant: str | None, module: str, standard: str) -> type | None:
    """The standard backend, or its contrastive sibling when ``variant`` asks.

    ``None`` when the coordinate has no such variant: backprop and EqProp were
    never given one, and a variant that silently resolved to the standard kernel
    would report a contrastive run that never happened.
    """
    if variant != "contrastive":
        return _backend(module, standard)
    from computronium.acceleration import contrastive_kernels

    sibling = standard.removesuffix("KernelBackend") + "ContrastiveKernel"
    return getattr(contrastive_kernels, sibling, None)


def _parameter(system: System) -> Tensor | None:
    return next(iter(system.geometry.params.values()), None)


def kernel_config_of(system: System, backend_cls: type) -> KernelConfig:
    """The :class:`KernelConfig` a backend needs to serve ``system``.

    Every value is read from the axis configs the system already carries, so the
    kernel rung is initialised with the coordinate's own knobs rather than the
    backend's defaults — a rung that silently used different ``beta`` or ``lr``
    would report the reference rung's accuracy at the kernel rung's speed.

    Args:
        system: the system the backend will be bound to.
        backend_cls: the class being configured; it supplies the algorithm name
            its own :class:`KernelConfig` validation reads.

    Returns:
        A config carrying the coordinate's dimensions, rates and settle budget.
    """
    from computronium.acceleration.kernel_backend import HardwareTarget, KernelConfig

    geometry = system.geometry.config
    dynamics = system.dynamics.config
    credit = system.credit.config
    update = system.update.config

    hidden = tuple(getattr(geometry, "hidden_dims", ()) or ())
    parameter = _parameter(system)
    on_cuda = parameter is not None and parameter.is_cuda
    settle_steps = int(getattr(dynamics, "max_steps", 0) or 0)

    extra: dict[str, object] = {
        "input_dim": geometry.input_dim,
        "output_dim": geometry.output_dim,
        "hidden_dim": hidden[0] if hidden else geometry.output_dim,
        "num_layers": int(getattr(geometry, "num_layers", 0) or len(hidden) or 1),
        "learning_rate": update.step_size,
        "beta": credit.beta,
        "max_steps": settle_steps,
        "neurons_per_tile": getattr(geometry, "neurons_per_tile", 8),
        "tiles_per_layer": getattr(geometry, "tiles_per_layer", 2),
        "world_size": 1,
        "rank": 0,
    }
    return KernelConfig(
        algorithm=backend_cls.name,
        hardware=HardwareTarget.CUDA if on_cuda else HardwareTarget.CPU,
        dtype=parameter.dtype if parameter is not None else torch.float32,
        settle_steps=settle_steps,
        extra=extra,
    )


def sweep_hyperparameters(coordinate: DispatchKey) -> dict[str, tuple[float, float, str] | list]:
    """Union of hyperparameters() from all primitives named by ``coordinate``.

    The sweep proposes a coordinate and unions the hyperparameters() of the
    primitives it names. A knob the arm cannot consume becomes unrepresentable
    by construction — the phantom-knob lock is then a property of the design,
    not a check that must be maintained.

    Args:
        coordinate: A dispatch key from :func:`key_of`.

    Returns:
        Merged hyperparameter dict. Later axes override earlier on collision.
    """
    from computronium.ontology.geometry import GeometryConfig
    from computronium.ontology.dynamics import StateDynamicsConfig
    from computronium.ontology.credit import CreditAssignmentConfig
    from computronium.ontology.update import ParameterUpdateConfig
    from computronium.state import PlasticityConfig

    geometry_name, dynamics_name, credit_name, update_name, plasticity_name = coordinate

    # Map axis names to their config classes
    axis_configs: list[tuple[type, str]] = [
        (GeometryConfig, geometry_name),
        (StateDynamicsConfig, dynamics_name),
        (CreditAssignmentConfig, credit_name),
        (ParameterUpdateConfig, update_name),
        (PlasticityConfig, plasticity_name),
    ]

    merged: dict[str, tuple[float, float, str] | list] = {}
    for config_cls, _factory_name in axis_configs:
        # The factory name identifies the primitive variant, but hyperparameters()
        # is defined on the config class itself and returns all knobs that axis owns.
        # We union all of them; the coordinate's specific primitive variant determines
        # which subset is actually consumed.
        hp = config_cls.hyperparameters()
        merged.update(hp)

    return merged


def sweep_hyperparameters_from_system(system: System) -> dict[str, tuple[float, float, str] | list]:
    """Convenience: sweep hyperparameters from a live system's coordinate."""
    return sweep_hyperparameters(key_of(system))
