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

import importlib

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
from computronium.acceleration.kernel_backend import (
    AlgorithmFamily,
    HardwareTarget,
    KernelBackend,
    KernelConfig,
    KernelRegistry,
    LocalityLevel,
    infer_algorithm_family,
)
from computronium.acceleration.contrastive_kernels import register_contrastive_kernels
from computronium.core.utils.activations import (
    cross_entropy,
    get_backend,
    softmax,
    spectral_normalize,
    to_numpy,
)


def _register_standard_kernels() -> None:
    """Register standard kernel backends with KernelRegistry.

    Replaces the former families.register_all() binding table. Each backend is
    registered explicitly so the registry contents don't depend on import order.
    """
    standard_kernels: tuple[tuple[AlgorithmFamily, str, str], ...] = (
        (AlgorithmFamily.EQPROP, "computronium.acceleration.eqprop_kernel_backend", "EqPropKernelBackend"),
        (AlgorithmFamily.BACKPROP, "computronium.acceleration.backprop_kernels", "BackpropKernelBackend"),
        (AlgorithmFamily.FA, "computronium.acceleration.fa_kernels", "FAKernelBackend"),
        (AlgorithmFamily.HEBBIAN, "computronium.acceleration.hebbian_kernels", "HebbianKernelBackend"),
        (AlgorithmFamily.FF, "computronium.acceleration.ff_kernels", "FFKernelBackend"),
        (AlgorithmFamily.PEPITA, "computronium.acceleration.ff_kernels", "PEPITAKernelBackend"),
        (AlgorithmFamily.TP, "computronium.acceleration.tp_kernels", "TPKernelBackend"),
        (AlgorithmFamily.PC, "computronium.acceleration.pc_kernels", "PCKernelBackend"),
        (AlgorithmFamily.SNN, "computronium.acceleration.snn_kernels", "SNNKernelBackend"),
        (AlgorithmFamily.TILE, "computronium.acceleration.tile_kernels", "TileKernelBackend"),
        (AlgorithmFamily.MEP, "computronium.acceleration.mep_kernels", "MEPKernelBackend"),
        (AlgorithmFamily.O1MEMORY, "computronium.acceleration.mep_kernels", "O1MemoryEPv2KernelBackend"),
    )
    for family, module_path, class_name in standard_kernels:
        backend_cls = getattr(importlib.import_module(module_path), class_name)
        for hardware in HardwareTarget:
            KernelRegistry.register(family, hardware, backend_cls)
    # Also register contrastive kernels under their distinct family keys
    register_contrastive_kernels()


def get_algorithm_kernels() -> dict[str, type[object]]:  # ruff: ignore[non-empty-init-module]
    """Bind every family and return its backend class, keyed by family value."""
    # This function is kept for backwards compatibility but the dispatch layer
    # now uses coordinate matching (select_backend_class) instead of family lookups.
    standard_kernels: tuple[tuple[str, str, str], ...] = (
        ("eqprop", "computronium.acceleration.eqprop_kernel_backend", "EqPropKernelBackend"),
        ("backprop", "computronium.acceleration.backprop_kernels", "BackpropKernelBackend"),
        ("fa", "computronium.acceleration.fa_kernels", "FAKernelBackend"),
        ("hebbian", "computronium.acceleration.hebbian_kernels", "HebbianKernelBackend"),
        ("ff", "computronium.acceleration.ff_kernels", "FFKernelBackend"),
        ("pepita", "computronium.acceleration.ff_kernels", "PEPITAKernelBackend"),
        ("tp", "computronium.acceleration.tp_kernels", "TPKernelBackend"),
        ("pc", "computronium.acceleration.pc_kernels", "PCKernelBackend"),
        ("snn", "computronium.acceleration.snn_kernels", "SNNKernelBackend"),
        ("tile", "computronium.acceleration.tile_kernels", "TileKernelBackend"),
        ("mep", "computronium.acceleration.mep_kernels", "MEPKernelBackend"),
        ("o1memory", "computronium.acceleration.mep_kernels", "O1MemoryEPv2KernelBackend"),
    )
    out: dict[str, type] = {}
    for name, module_path, class_name in standard_kernels:
        out[name] = getattr(importlib.import_module(module_path), class_name)
    # Also include contrastive kernels
    from computronium.acceleration.contrastive_kernels import get_contrastive_kernels
    out.update(get_contrastive_kernels())
    return out


# The one stated call site for the binding layer (TODO36 §4.3). Every family is
# bound here, explicitly, so no kernel module registers as an import side effect
# and the registry's contents cannot depend on which module was imported first.
_register_standard_kernels()  # ruff: ignore[non-empty-init-module]  (the stated call site)

__all__ = [
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
    "softmax",
    "spectral_normalize",
    "target_propagation_target",
    "to_numpy",
    "triton_rung_available",
    "triton_stack_available",
]
