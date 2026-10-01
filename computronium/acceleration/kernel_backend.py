"""The binding layer: stateful rungs, bound to a family and a hardware target.

``KernelRegistry`` holds rungs that need state -- ``initialize``, ``bind_system``,
and the export path's need to serialise a *bound* backend. It is **not** the
training dispatch: every training run goes through
:func:`computronium.acceleration.dispatch.select_backend`, which is driven by
``ImplementationSpec`` and knows about technologies, promotion status and parity
tolerances. This module knows about classes and instances, and nothing else.

The bindings themselves live in one table,
:data:`computronium.acceleration.families.BINDINGS`, applied by
:func:`computronium.acceleration.families.register_all`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import TYPE_CHECKING, ClassVar, Protocol, runtime_checkable

import numpy as np
import torch
from torch import Tensor

if TYPE_CHECKING:
    from collections.abc import Callable

    from computronium.ontology import System


class AlgorithmFamily(StrEnum):
    """Supported bio-plausible algorithm families."""

    EQPROP = "eqprop"
    FA = "fa"
    HEBBIAN = "hebbian"
    FF = "ff"
    PEPITA = "pepita"
    TP = "tp"
    PC = "pc"
    SNN = "snn"
    TILE = "tile"
    MEP = "mep"
    PCALM = "pcalm"
    O1MEMORY = "o1memory"
    BACKPROP = "backprop"
    # Contrastive kernel families (distinct from standard backends for coexistence)
    FA_CONTRASTIVE = "fa_contrastive"
    HEBBIAN_CONTRASTIVE = "hebbian_contrastive"
    FF_CONTRASTIVE = "ff_contrastive"
    PEPITA_CONTRASTIVE = "pepita_contrastive"
    TP_CONTRASTIVE = "tp_contrastive"
    PC_CONTRASTIVE = "pc_contrastive"
    SNN_CONTRASTIVE = "snn_contrastive"
    TILE_CONTRASTIVE = "tile_contrastive"
    MEP_CONTRASTIVE = "mep_contrastive"
    O1MEMORY_CONTRASTIVE = "o1memory_contrastive"


class HardwareTarget(StrEnum):
    """Supported hardware targets."""

    CPU = "cpu"
    CUDA = "cuda"
    TRITON = "triton"
    FPGA = "fpga"
    NEUROMORPHIC = "neuromorphic"
    OPTICAL = "optical"
    CROSSBAR = "crossbar"
    QUANTUM = "quantum"


class LocalityLevel(StrEnum):
    """Credit assignment locality level."""

    GLOBAL = "global"
    LAYERWISE = "layerwise"
    LOCAL = "local"
    EQUILIBRIUM = "equilibrium"
    FORWARD_ONLY = "forward_only"


@dataclass(frozen=True, slots=True)
class KernelConfig:
    """Configuration for a kernel backend.

    Args:
        algorithm: Algorithm family this kernel implements.
        hardware: Target hardware backend.
        dtype: Computation dtype (default float32).
        use_autograd: Whether to use autograd (False = O(1) contrastive path).
        settle_steps: Number of settling steps for algorithms with settling dynamics.
        beta: Nudge strength (EqProp, MEP, Contrastive).
        gamma: Decay/leak factor.
        spectral_norm: Whether to apply spectral normalization.
        **kwargs: Algorithm-specific extra parameters.
    """

    algorithm: AlgorithmFamily
    hardware: HardwareTarget
    dtype: torch.dtype = torch.float32
    use_autograd: bool = False
    settle_steps: int = 0
    beta: float = 0.0
    gamma: float = 1.0
    spectral_norm: bool = False
    # Algorithm-specific extras (validated at backend construction)
    # FA: dropout_prob, feedback_mode
    # Hebbian: use_oja, learning_rate
    # FF: threshold, num_layers
    # PEPITA: feedback_matrix_scale  # ruff: ignore[commented-out-code]
    # TP: target_lr, inverse_net_lr
    # PC: infer_steps, eta_infer
    # SNN: num_steps, spike_grad, tau_mem, tau_syn
    # Tile: neurons_per_tile, tiles_per_layer, num_hidden_layers
    # MEP: ns_steps, rank_frac, fisher_damping, loss_type
    # O1Memory: loss_type, softmax_temperature
    # Backprop: grad_clip, accumulation_steps
    extra: dict[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.algorithm == AlgorithmFamily.EQPROP and self.settle_steps == 0:
            object.__setattr__(self, "settle_steps", 30)
        if (
            self.algorithm in {AlgorithmFamily.MEP, AlgorithmFamily.O1MEMORY}
            and self.settle_steps == 0
        ):
            object.__setattr__(self, "settle_steps", 30)


@runtime_checkable
class KernelBackend(Protocol):
    """Hardware-agnostic kernel backend for a bio-plausible algorithm family.

    Implementations must be stateless or reset between training steps.
    All tensor operations should respect the configured dtype and device.
    """

    name: AlgorithmFamily
    supported_dtypes: tuple[torch.dtype, ...]
    supports_autograd: bool
    requires_settle: bool
    memory_complexity: str  # "O(1)", "O(L)", "O(L*H)"
    locality_level: LocalityLevel

    def initialize(self, config: KernelConfig) -> None: ...
    def bind_system(self, system: System) -> None: ...
    def train_step(self, x: Tensor, y: Tensor) -> dict[str, float]: ...
    def forward(self, *args: object, **kwargs: object) -> object: ...
    def backward(self, *args: object, **kwargs: object) -> object: ...
    def update_weights(self, *args: object, **kwargs: object) -> None: ...
    def get_memory_stats(self) -> dict[str, float]: ...
    def get_settle_telemetry(self) -> dict[str, object] | None: ...


# Registry
class KernelRegistry:
    """Global registry for kernel backends with auto-selection and auto-tuning logic."""

    _backends: ClassVar[dict[AlgorithmFamily, dict[HardwareTarget, type]]] = {}
    _instances: ClassVar[dict[tuple[AlgorithmFamily, HardwareTarget], object]] = {}
    # Auto-tuning cache: (algorithm, hardware, op_name, shape) -> best_hardware
    _autotune_cache: ClassVar[
        dict[
            tuple[AlgorithmFamily, HardwareTarget, str, tuple[int, ...]], HardwareTarget
        ]
    ] = {}
    # Benchmark results: (algorithm, hardware, op_name, shape) -> list of (hardware, time_ms)
    _benchmark_cache: ClassVar[
        dict[
            tuple[AlgorithmFamily, HardwareTarget, str, tuple[int, ...]],
            list[tuple[HardwareTarget, float]],
        ]
    ] = {}

    @classmethod
    def register(
        cls,
        algorithm: AlgorithmFamily,
        hardware: HardwareTarget,
        backend_cls: type,
    ) -> None:
        """Register a kernel backend class."""
        if algorithm not in cls._backends:
            cls._backends[algorithm] = {}
        cls._backends[algorithm][hardware] = backend_cls

    @classmethod
    def get(cls, algorithm: AlgorithmFamily, hardware: HardwareTarget) -> object | None:
        """Get or create a backend instance."""
        key = (algorithm, hardware)
        if key in cls._instances:
            return cls._instances[key]

        if algorithm not in cls._backends or hardware not in cls._backends[algorithm]:
            return None

        backend_cls = cls._backends[algorithm][hardware]
        instance = backend_cls()
        cls._instances[key] = instance
        return instance

    @classmethod
    def get_best(
        cls, algorithm: AlgorithmFamily, preferred: HardwareTarget | str = "cuda"
    ) -> object | None:
        """Get best available backend for algorithm, falling back through priority.

        Priority: TRITON > CUDA > CPU
        """
        preferred_hw = (
            HardwareTarget(preferred) if isinstance(preferred, str) else preferred
        )

        # Try preferred first
        backend = cls.get(algorithm, preferred_hw)
        if backend is not None:
            return backend

        # Fallback priority
        for hw in (HardwareTarget.TRITON, HardwareTarget.CUDA, HardwareTarget.CPU):
            backend = cls.get(algorithm, hw)
            if backend is not None:
                return backend

        return None

    @classmethod
    def get_best_for_shape(
        cls,
        algorithm: AlgorithmFamily,
        op_name: str,
        shape: tuple[int, ...],
        benchmark_fn: Callable[[object, tuple[int, ...]], float] | None = None,
        warmup_runs: int = 3,
        benchmark_runs: int = 10,
    ) -> object | None:
        """Get best backend for a specific operation shape using auto-tuning.

        Args:
            algorithm: Algorithm family
            op_name: Operation name (e.g., "forward", "backward", "update_weights")
            shape: Input tensor shape
            benchmark_fn: Optional custom benchmark function. If None, uses default timing.
            warmup_runs: Number of warmup iterations
            benchmark_runs: Number of benchmark iterations

        Returns:
            Best backend instance for this operation/shape combination
        """
        cache_key = (algorithm, op_name, shape)

        # Check auto-tune cache first
        if cache_key in cls._autotune_cache:
            best_hw = cls._autotune_cache[cache_key]
            return cls.get(algorithm, best_hw)

        # Get available hardware targets for this algorithm
        available_hw = cls.list_for(algorithm)
        if not available_hw:
            return None

        # Priority order for fallback
        priority_order = [
            HardwareTarget.TRITON,
            HardwareTarget.CUDA,
            HardwareTarget.CPU,
        ]
        candidate_hw = [hw for hw in priority_order if hw in available_hw]

        if len(candidate_hw) == 1:
            # Only one option, no need to benchmark
            cls._autotune_cache[cache_key] = candidate_hw[0]
            return cls.get(algorithm, candidate_hw[0])

        # Benchmark each backend for this shape
        best_hw = cls._benchmark_backends(
            algorithm,
            op_name,
            shape,
            candidate_hw,
            benchmark_fn,
            warmup_runs,
            benchmark_runs,
        )

        cls._autotune_cache[cache_key] = best_hw
        return cls.get(algorithm, best_hw)

    @classmethod
    def _benchmark_backends(
        cls,
        algorithm: AlgorithmFamily,
        op_name: str,
        shape: tuple[int, ...],
        candidate_hw: list[HardwareTarget],
        benchmark_fn: Callable[[object, tuple[int, ...]], float] | None,
        warmup_runs: int,
        benchmark_runs: int,
    ) -> HardwareTarget:
        """Benchmark multiple backends and return the fastest."""
        bench_key = (algorithm, op_name, shape)
        results = []

        for hw in candidate_hw:
            backend = cls.get(algorithm, hw)
            if backend is None:
                continue

            try:  # noqa: PLR0915
                if benchmark_fn is not None:
                    # Use custom benchmark function
                    time_ms = benchmark_fn(backend, shape)
                else:
                    # Default: time the forward pass with dummy inputs
                    time_ms = cls._default_benchmark(
                        backend, op_name, shape, warmup_runs, benchmark_runs
                    )

                if time_ms > 0 and not np.isinf(time_ms):
                    results.append((hw, time_ms))
            except Exception:  # noqa: S112 - try next backend
                # Backend failed, skip
                continue

        # Cache benchmark results
        if results:
            cls._benchmark_cache[bench_key] = results

        if not results:
            # All failed, return first candidate as fallback
            return candidate_hw[0]

        # Return fastest
        return min(results, key=lambda x: x[1])[0]

    @classmethod
    def _default_benchmark(
        cls,
        backend: object,
        op_name: str,
        shape: tuple[int, ...],
        warmup_runs: int,
        benchmark_runs: int,
    ) -> float:
        """Default benchmark using forward pass with random inputs."""
        import time

        # Create dummy inputs based on shape
        if hasattr(backend, "initialize"):
            # Try to initialize with minimal config
            try:
                from computronium.acceleration.kernel_backend import (
                    HardwareTarget,
                    KernelConfig,
                )

                config = KernelConfig(
                    algorithm=backend.name
                    if hasattr(backend, "name")
                    else AlgorithmFamily.BACKPROP,
                    hardware=HardwareTarget.CPU,
                    extra={"num_layers": 2, "hidden_dim": shape[-1] if shape else 256},
                )
                backend.initialize(config)
            except Exception:  # noqa: S110 - fallback to default backend
                pass

        # Get the operation method
        method = getattr(backend, op_name, None)
        if method is None:
            return float("inf")

        # Warmup
        try:
            for _ in range(warmup_runs):
                if op_name == "forward":
                    x = torch.randn(*shape, device="cpu")
                    _ = method(x)
                else:
                    # For other ops, try with minimal args
                    _ = method()
        except Exception:
            return float("inf")

        # Benchmark
        times = []
        for _ in range(benchmark_runs):
            start = time.perf_counter()
            try:
                if op_name == "forward":
                    x = torch.randn(*shape, device="cpu")
                    _ = method(x)
                else:
                    _ = method()
            except Exception:
                return float("inf")
            elapsed = time.perf_counter() - start
            times.append(elapsed * 1000)  # ms

        return float(np.mean(times))

    @classmethod
    def clear_autotune_cache(cls) -> None:
        """Clear the auto-tuning cache (e.g., when hardware changes)."""
        cls._autotune_cache.clear()
        cls._benchmark_cache.clear()

    @classmethod
    def get_benchmark_results(
        cls, algorithm: AlgorithmFamily, op_name: str, shape: tuple[int, ...]
    ) -> list[tuple[HardwareTarget, float]] | None:
        """Get cached benchmark results for an operation/shape."""
        return cls._benchmark_cache.get((algorithm, op_name, shape))

    @classmethod
    def has(cls, algorithm: AlgorithmFamily, hardware: HardwareTarget) -> bool:
        """Check if a backend is registered."""
        return algorithm in cls._backends and hardware in cls._backends[algorithm]

    @classmethod
    def list_for(cls, algorithm: AlgorithmFamily) -> list[HardwareTarget]:
        """List registered hardware targets for an algorithm."""
        return list(cls._backends.get(algorithm, {}).keys())

    @classmethod
    def list_all(cls) -> dict[AlgorithmFamily, list[HardwareTarget]]:
        """List all registered backends."""
        return {alg: list(hw.keys()) for alg, hw in cls._backends.items()}

    @classmethod
    def clear_cache(cls) -> None:
        """Clear instantiated backends (for testing/reload)."""
        cls._instances.clear()


class LinearView:
    """One dense layer of a geometry, presented the way a kernel backend reads it.

    A backend wants a callable layer plus writable ``weight``/``bias`` and the
    two widths. The ontology's geometries keep those tensors in
    ``geometry.params`` under layer-indexed keys (``0.weight``, ``0.bias``,
    ``2.weight``, …) and expose no submodules, so nine backends each looked for
    a module the geometry does not have, found nothing, and went on to train a
    *private* copy of the network — a rung that reported plausible metrics for
    weights the system never read.

    A view is not a copy. It is built around the geometry's own tensor, so an
    in-place update on either side is visible to the other and
    ``system.forward()`` reflects what the kernel learned. ``requires_grad`` is
    cleared because a kernel rung does not backprop, and autograd's version
    counter does not follow a write made through a second tensor object; the
    reference rung, which does backprop, never sees these views.

    Attributes:
        weight: the geometry's weight tensor, shared.
        bias: the geometry's bias tensor, shared; ``None`` for a bias-free layer.
        source: the geometry parameter keys this view stands for.
        in_features: the weight's second dimension.
        out_features: the weight's first dimension.
    """

    __slots__ = ("bias", "in_features", "out_features", "source", "weight")

    def __init__(
        self, weight: Tensor, bias: Tensor | None, source: tuple[str, str]
    ) -> None:
        self.weight = weight
        self.bias = bias
        self.out_features, self.in_features = weight.shape
        self.source = source

    def __call__(self, x: Tensor) -> Tensor:
        return torch.nn.functional.linear(x, self.weight, self.bias)


def _param_order(prefix: str) -> tuple[int, float | str]:
    """Sort layer keys by their index when they have one, lexically otherwise."""
    return (0, float(prefix)) if prefix.isdigit() else (1, prefix)


def linear_views(geometry: object) -> list[LinearView]:
    """A geometry's dense layers, as modules that *share its storage*.

    Every kernel backend wants the same two things from a geometry: a callable
    layer stack and writable weight and bias tensors. The ontology's geometries
    provide the tensors — in ``geometry.params``, keyed by layer index as
    ``0.weight``/``0.bias``/``2.weight``/… — and provide no submodules. Nine
    backends each looked for a submodule the geometry does not have, found
    nothing, and went on to train a *private* copy of the network: a rung that
    reported plausible metrics for weights the system never read.

    These are views, not copies. Each ``nn.Linear`` is constructed around the
    geometry's own tensor, so an in-place update on either side is visible to the
    other and ``system.forward()`` reflects what the kernel learned. The views
    carry ``requires_grad=False`` because a kernel rung does not backprop, and
    autograd's version counter does not follow a write through a second tensor
    object; the reference rung, which does backprop, never sees these views.

    Args:
        geometry: an axis geometry, or anything else exposing ``params``.

    Returns:
        The dense layers in index order; empty when the geometry has none.
    """
    params = getattr(geometry, "params", None)
    if params is None:
        return list(getattr(geometry, "layers", []) or [])

    grouped: dict[str, dict[str, Tensor]] = {}
    for name, tensor in params.items():
        prefix, _, role = name.rpartition(".")
        if role in {"weight", "bias"}:
            grouped.setdefault(prefix, {})[role] = tensor

    views: list[LinearView] = []
    for prefix in sorted(grouped, key=_param_order):
        roles = grouped[prefix]
        weight = roles.get("weight")
        if weight is None or weight.dim() != 2:
            continue
        bias = roles.get("bias")
        views.append(
            LinearView(
                weight=weight.requires_grad_(False),
                bias=bias.requires_grad_(False) if bias is not None else None,
                source=(f"{prefix}.weight", f"{prefix}.bias"),
            )
        )
    return views


def infer_algorithm_family(model_name: str) -> AlgorithmFamily | None:
    """Infer algorithm family from model registry name."""
    name = model_name.lower()

    # Ordered by specificity: more specific prefixes first
    family_map = [
        (("eqprop", "looped"), AlgorithmFamily.EQPROP),
        (("tile",), AlgorithmFamily.TILE),
        (("predictive", "pc"), AlgorithmFamily.PC),
        (("spiking", "snn", "stdp"), AlgorithmFamily.SNN),
        (("hebbian",), AlgorithmFamily.HEBBIAN),
        (("fa", "feedback", "dfa"), AlgorithmFamily.FA),
        (("forward_only", "forward_forward", "ff"), AlgorithmFamily.FF),
        (("pepita",), AlgorithmFamily.PEPITA),
        (("target", "tp"), AlgorithmFamily.TP),
        (("mep", "o1memory", "muon", "dion", "fisher"), AlgorithmFamily.MEP),
        (("backprop",), AlgorithmFamily.BACKPROP),
    ]

    for patterns, family in family_map:
        if any(p in name for p in patterns):
            return family
    return None


__all__ = [
    "AlgorithmFamily",
    "HardwareTarget",
    "KernelBackend",
    "KernelConfig",
    "KernelRegistry",
    "LinearView",
    "LocalityLevel",
    "infer_algorithm_family",
    "linear_views",
]
