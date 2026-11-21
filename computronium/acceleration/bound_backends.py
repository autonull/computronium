"""Bound-rung backends: the algorithm's step run on the system it is attached to.

Three coordinates have a declared kernel rung whose acceleration lives in the
axis primitives, not in a second training loop: PC-ALM's settle is the compiled
``pcalm_kernels`` loop inside :class:`PCALMDynamics`, the tile mesh runs through
:class:`TileGeometry`, and fast weights step through
:class:`FastWeightPlasticity`.  What was missing was the *arm*: a backend class
that binds the composed system and runs one step through it.  Without one the
coordinate had no dispatch target and the kernel rung was unreachable.

These classes hold no network of their own.  ``bind_system`` stores the system
and ``train_step`` runs the same axes the reference rung runs, which is the
contract ``tests/acceleration/test_backend_reach.py`` enforces: an arm that
trains a private copy reports metrics the system never reads.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from computronium.acceleration.kernel_backend import AlgorithmFamily, LocalityLevel

if TYPE_CHECKING:
    from collections.abc import Callable
    from typing import Protocol

    from torch import Tensor

    from computronium.acceleration.kernel_backend import KernelConfig
    from computronium.ontology import (
        CreditAssignment,
        Geometry,
        ParameterUpdate,
        StateDynamics,
        Substrate,
    )

    class _Plasticity(Protocol):
        def initial_psi(
            self, context: object, batch_size: int
        ) -> dict[str, Tensor]: ...

    class _JointAxes(Protocol):
        """The six axes and the context a plastic composition exposes."""

        substrate: Substrate
        geometry: Geometry
        dynamics: StateDynamics
        plasticity: _Plasticity
        credit: CreditAssignment
        update: ParameterUpdate
        loss_fn: Callable[[Tensor, Tensor], Tensor] | None

        @property
        def context(self) -> object: ...


__all__ = [
    "FastWeightKernelBackend",
    "PCALMKernelBackend",
    "TileMeshKernelBackend",
]


class _BoundSystemBackend:
    """A backend that runs the bound system's own composed training step.

    Subclasses declare the algorithm family, the locality of its credit, whether
    its law settles, and whether the composition is the 6-D (plastic) pipeline.
    The step itself is not duplicated: the axes carry the maths.
    """

    name: AlgorithmFamily
    supported_dtypes = ()
    supports_autograd = False
    requires_settle = False
    memory_complexity = "O(L)"
    available = True
    complexity_verified = False
    locality_level = LocalityLevel.LAYERWISE
    _plastic = False

    def __init__(self) -> None:
        self._config: KernelConfig | None = None
        self._system: _JointAxes | None = None

    def initialize(self, config: KernelConfig) -> None:
        self._config = config

    def bind_system(self, system: _JointAxes) -> None:
        self._system = system

    def train_step(self, x: Tensor, y: Tensor) -> dict[str, float]:
        from computronium.core.pipeline import run_train_step

        system = self._system
        if system is None:
            raise RuntimeError(f"{type(self).__name__} is not bound to a system")
        axes = (
            system.substrate,
            system.geometry,
            system.dynamics,
            system.credit,
            system.update,
        )
        if not self._plastic:
            return run_train_step(*axes, x, y, loss_fn=system.loss_fn)
        psi = system.plasticity.initial_psi(system.context, batch_size=x.shape[0])
        return run_train_step(
            *axes,
            x,
            y,
            plasticity=system.plasticity,
            psi=psi,
            context=system.context,
            loss_fn=system.loss_fn,
        )

    def get_memory_stats(self) -> dict[str, float | None]:
        return {"params_mb": None, "activations_mb": None}

    def get_settle_telemetry(self) -> dict[str, object] | None:
        return None


class FastWeightKernelBackend(_BoundSystemBackend):
    """Fast weights: the outer-product memory steps through the P axis."""

    name = AlgorithmFamily.HEBBIAN
    supports_autograd = True
    locality_level = LocalityLevel.LOCAL
    _plastic = True


class PCALMKernelBackend(_BoundSystemBackend):
    """PC-ALM: the primal-dual settle runs as the compiled PC-ALM loop."""

    name = AlgorithmFamily.PCALM
    requires_settle = True
    locality_level = LocalityLevel.LAYERWISE


class TileMeshKernelBackend(_BoundSystemBackend):
    """TileNet: one step over the tile-mesh geometry's own weighted graph."""

    name = AlgorithmFamily.TILE
    supports_autograd = True
    locality_level = LocalityLevel.LAYERWISE
