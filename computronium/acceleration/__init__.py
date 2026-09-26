"""
Acceleration Module for Bioplausible

Provides multiple acceleration backends for Equilibrium Propagation and
all bio-plausible algorithm families:
EqProp, FA, Hebbian, FF, PEPITA, TP, PC, SNN, Tile, MEP, O1Memory, Backprop.

Backends (in order of priority for speed):
    1. Triton Kernels: Custom GPU kernels for fused operations (fastest)
    2. CuPy: NumPy-compatible GPU arrays via CUDA
    3. torch.compile: PyTorch 2.0+ JIT compilation
    4. Pure PyTorch: Standard autograd (fallback)
    5. Pure NumPy: CPU-only kernel (portability)

Usage:
    from computronium.acceleration import (
        get_optimal_backend,
        compile_model,
        HAS_CUPY,
        TRITON_IMPORTED,
        KernelBackend,
        KernelRegistry,
        KernelConfig,
        AlgorithmFamily,
        HardwareTarget,
    )

    # Check available backends
    >>> from computronium.core.logging import get_logger
    >>> get_logger().info("CuPy: %s, Triton: %s", HAS_CUPY, TRITON_IMPORTED)
"""

from computronium.acceleration.availability import (
    CompileState,
    compile_report,
    triton_rung_available,
    triton_stack_available,
)
from computronium.acceleration.backends import (
    HAS_CUPY,
    TRITON_IMPORTED,
    AutoDispatcher,
    BackendBenchmark,
    BackendDetector,
    BackendType,
    CupyChecker,
    KernelProfiler,
    TritonChecker,
    check_cupy_available,
    check_triton_available,
    dispatch_kernel,
    enable_tf32,
    get_dispatcher,
    get_optimal_backend,
    kernel_available,
    profile_kernel,
)
from computronium.acceleration.compile import (
    compile_model,
    compile_model_with_preset,
    compile_settling_loop,
    get_compile_config,
)
from computronium.acceleration.contrastive_primitives import (
    conductance_matmul,
    forward_forward_goodness,
    pepita_error_modulation,
    phase_encode,
    target_propagation_target,
)
from computronium.acceleration.families import (
    BINDINGS,
    backends_by_family,
    register_all,
)
from computronium.acceleration.kernel_backend import (
    AlgorithmFamily,
    HardwareTarget,
    KernelBackend,
    KernelConfig,
    KernelRegistry,
    LocalityLevel,
    infer_algorithm_family,
)
from computronium.core.utils.activations import (
    cross_entropy,
    get_backend,
    softmax,
    spectral_normalize,
    to_numpy,
)


def get_kernel_classes() -> tuple[type[object], type[object]]:  # ruff: ignore[non-empty-init-module]
    """Lazily import kernel classes to avoid circular imports."""
    from computronium.acceleration.kernels import EqPropKernel as _EqPropKernel
    from computronium.acceleration.kernels import (
        EqPropKernelBPTT as _EqPropKernelBPTT,
    )

    return _EqPropKernel, _EqPropKernelBPTT


def get_triton_ops() -> type[object] | None:  # ruff: ignore[non-empty-init-module]
    """Lazily import Triton ops, returning None if unavailable."""
    try:
        from computronium.acceleration.triton_kernels import (
            TritonEqPropOps as _TritonEqPropOps,
        )
    except ImportError:
        return None
    return _TritonEqPropOps


def get_algorithm_kernels() -> dict[str, type[object]]:  # ruff: ignore[non-empty-init-module]
    """Bind every family and return its backend class, keyed by family value."""
    return backends_by_family()


# The one stated call site for the binding layer (TODO36 §4.3). Every family is
# bound here, explicitly, so no kernel module registers as an import side effect
# and the registry's contents cannot depend on which module was imported first.
register_all()  # ruff: ignore[non-empty-init-module]  (the stated call site)

__all__ = [
    "BINDINGS",
    "HAS_CUPY",
    "TRITON_IMPORTED",
    "AlgorithmFamily",
    "AutoDispatcher",
    "BackendBenchmark",
    "BackendDetector",
    "BackendType",
    "CompileState",
    "CupyChecker",
    "HardwareTarget",
    "KernelBackend",
    "KernelConfig",
    "KernelProfiler",
    "KernelRegistry",
    "LocalityLevel",
    "TritonChecker",
    "check_cupy_available",
    "check_triton_available",
    "compile_model",
    "compile_model_with_preset",
    "compile_report",
    "compile_settling_loop",
    "conductance_matmul",
    "cross_entropy",
    "dispatch_kernel",
    "enable_tf32",
    "forward_forward_goodness",
    "get_algorithm_kernels",
    "get_backend",
    "get_compile_config",
    "get_dispatcher",
    "get_kernel_classes",
    "get_optimal_backend",
    "get_triton_ops",
    "infer_algorithm_family",
    "kernel_available",
    "pepita_error_modulation",
    "phase_encode",
    "profile_kernel",
    "register_all",
    "softmax",
    "spectral_normalize",
    "target_propagation_target",
    "to_numpy",
    "triton_rung_available",
    "triton_stack_available",
]
