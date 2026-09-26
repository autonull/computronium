"""One table binding each algorithm family to the backend class that serves it.

`KernelRegistry` is the *binding layer*: it holds stateful rungs that need
``initialize``, ``set_model_ref`` and the export path's ability to serialise a
bound backend. It is not the training dispatch — that is
:func:`computronium.acceleration.dispatch.select_backend`, which serves every
training run and is driven by ``ImplementationSpec``.

Before this module, the binding lived in three places that no reader could find
together: a ``for hw in HardwareTarget: KernelRegistry.register(...)`` loop at the
bottom of each of ten ``*_kernels`` modules, a side-effect import in
``acceleration/__init__.py``, and a second, differently-keyed list in
``get_algorithm_kernels()``. Worse, the registry's contents depended on import
order: asking Layer A a question (``all_specs()``) imported
``local_goodness/kernel.py``, which imported ``fa_kernels``, which registered the
FA family. **The second system's contents changed when you queried the first.**

Now there is one table, one function, and one stated call site.
"""

from __future__ import annotations

import importlib
from dataclasses import dataclass

from computronium.acceleration.kernel_backend import (
    AlgorithmFamily,
    HardwareTarget,
    KernelRegistry,
)

__all__ = ["BINDINGS", "FamilyBinding", "backends_by_family", "register_all"]


@dataclass(frozen=True, slots=True)
class FamilyBinding:
    """Which class serves which family, and where it lives.

    Attributes:
        family: the family the backend is bound to.
        module: importable module path holding the class.
        backend: the class name inside that module.

    A family has at most one binding, because ``KernelRegistry`` keys on
    ``(family, hardware)`` and a second row for the same family would displace
    the first. ``ThreeFactorKernelBackend`` is a Hebbian variant and is
    therefore reachable by direct import only — registering it would silently
    replace ``HebbianKernelBackend`` for the whole family, which is the kind of
    quiet substitution TODO36 §4.8 also objects to.
    """

    family: AlgorithmFamily
    module: str
    backend: str

    @property
    def key(self) -> tuple[AlgorithmFamily, str]:
        return self.family, self.backend


BINDINGS: tuple[FamilyBinding, ...] = (
    FamilyBinding(
        AlgorithmFamily.EQPROP,
        "computronium.acceleration.eqprop_kernel_backend",
        "EqPropKernelBackend",
    ),
    FamilyBinding(
        AlgorithmFamily.BACKPROP,
        "computronium.acceleration.backprop_kernels",
        "BackpropKernelBackend",
    ),
    FamilyBinding(
        AlgorithmFamily.FA,
        "computronium.acceleration.fa_kernels",
        "FAKernelBackend",
    ),
    FamilyBinding(
        AlgorithmFamily.HEBBIAN,
        "computronium.acceleration.hebbian_kernels",
        "HebbianKernelBackend",
    ),
    FamilyBinding(
        AlgorithmFamily.FF,
        "computronium.acceleration.ff_kernels",
        "FFKernelBackend",
    ),
    FamilyBinding(
        AlgorithmFamily.PEPITA,
        "computronium.acceleration.ff_kernels",
        "PEPITAKernelBackend",
    ),
    FamilyBinding(
        AlgorithmFamily.TP,
        "computronium.acceleration.tp_kernels",
        "TPKernelBackend",
    ),
    FamilyBinding(
        AlgorithmFamily.PC,
        "computronium.acceleration.pc_kernels",
        "PCKernelBackend",
    ),
    FamilyBinding(
        AlgorithmFamily.SNN,
        "computronium.acceleration.snn_kernels",
        "SNNKernelBackend",
    ),
    FamilyBinding(
        AlgorithmFamily.TILE,
        "computronium.acceleration.tile_kernels",
        "TileKernelBackend",
    ),
    FamilyBinding(
        AlgorithmFamily.MEP,
        "computronium.acceleration.mep_kernels",
        "MEPKernelBackend",
    ),
    FamilyBinding(
        AlgorithmFamily.O1MEMORY,
        "computronium.acceleration.mep_kernels",
        "O1MemoryEPv2KernelBackend",
    ),
)


def register_all() -> tuple[FamilyBinding, ...]:
    """Bind every family in :data:`BINDINGS` for every hardware target.

    Called once, explicitly, from ``computronium.acceleration``. Registration is
    no longer a side effect of importing a kernel module, so the registry's
    contents no longer depend on which module was imported first.

    Returns:
        The bindings that were registered.
    """
    for binding in BINDINGS:
        backend_cls = getattr(importlib.import_module(binding.module), binding.backend)
        for hardware in HardwareTarget:
            KernelRegistry.register(binding.family, hardware, backend_cls)
    return BINDINGS


def backends_by_family() -> dict[str, type]:
    """Every bound backend class, keyed by family value.

    The single naming table: ``get_algorithm_kernels`` derives from it, so a
    family name has one referent instead of one per layer.
    """
    out: dict[str, type] = {}
    for binding in BINDINGS:
        module = importlib.import_module(binding.module)
        out.setdefault(binding.family.value, getattr(module, binding.backend))
    return out
