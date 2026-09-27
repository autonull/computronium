"""Safe Triton kernel launch utilities.

Provides exception handling for Triton kernel launches, catching:
- OutOfResources: GPU resource exhaustion (shared memory, registers, threads)
- CompilationError: Shape mismatches, invalid kernel configuration
- InterpreterError: Runtime interpreter failures
- TritonError: Base class for other Triton errors

On any Triton error, falls back to a provided torch implementation or re-raises.
"""

from __future__ import annotations

import logging
import warnings
from typing import TYPE_CHECKING, Any, TypeVar

if TYPE_CHECKING:
    from collections.abc import Callable

logger = logging.getLogger(__name__)

T = TypeVar("T")


def _get_triton_exceptions() -> tuple[
    type[BaseException], type[BaseException], type[BaseException], type[BaseException]
]:
    """Lazily import Triton exception classes."""
    try:
        import triton
    except (ImportError, AttributeError):
        # Triton not available or version mismatch - return dummy classes
        class OutOfResourcesError(Exception):
            pass

        class CompilationErrorError(Exception):
            pass

        class InterpreterErrorError(Exception):
            pass

        class TritonErrorError(Exception):
            pass

        return (
            OutOfResourcesError,
            CompilationErrorError,
            InterpreterErrorError,
            TritonErrorError,
        )
    else:
        return (
            triton.OutOfResources,
            triton.CompilationError,
            triton.InterpreterError,
            triton.TritonError,
        )


OutOfResourcesError, CompilationErrorError, InterpreterErrorError, TritonErrorError = (
    _get_triton_exceptions()
)


def safe_triton_launch[T](
    kernel_fn: "Callable[..., T]",
    *args,
    grid: tuple[int, ...] | None = None,
    fallback_fn: "Callable[..., T] | None" = None,
    kernel_name: str = "unknown",
    **kwargs,
) -> T:
    """
    Launch a Triton kernel with proper exception handling.

    Catches:
    - OutOfResources: GPU resource exhaustion (shared memory, registers, threads)
    - CompilationError: Shape mismatches, invalid kernel configuration
    - InterpreterError: Runtime interpreter failures
    - TritonError: Base class for other Triton errors

    On any Triton error, falls back to the provided fallback_fn or re-raises.

    Args:
        kernel_fn: The compiled Triton kernel (JITFunction) to launch
        *args: Positional arguments for the kernel
        grid: Optional grid tuple for kernel launch (e.g., (grid_x, grid_y))
        fallback_fn: Optional fallback function (typically torch implementation)
        kernel_name: Name for logging
        **kwargs: Keyword arguments for the kernel (including block size constants)

    Returns:
        Result from kernel_fn or fallback_fn (typically None for in-place kernels)

    Raises:
        Exception: If no fallback_fn and kernel fails
    """
    try:
        if grid is not None:
            # Triton kernel launch with grid
            kernel_fn[grid](*args, **kwargs)
        else:
            # Regular function call
            kernel_fn(*args, **kwargs)
    except OutOfResourcesError as exc:
        msg = f"Triton kernel '{kernel_name}' out of resources: {exc}"
        logger.warning(msg)
        warnings.warn(msg, RuntimeWarning)
        if fallback_fn is not None:
            return fallback_fn(*args, **kwargs)
        raise
    except CompilationErrorError as exc:
        msg = f"Triton kernel '{kernel_name}' compilation error (likely shape mismatch): {exc}"
        logger.warning(msg)
        warnings.warn(msg, RuntimeWarning)
        if fallback_fn is not None:
            return fallback_fn(*args, **kwargs)
        raise
    except InterpreterErrorError as exc:
        msg = f"Triton kernel '{kernel_name}' interpreter error: {exc}"
        logger.warning(msg)
        warnings.warn(msg, RuntimeWarning)
        if fallback_fn is not None:
            return fallback_fn(*args, **kwargs)
        raise
    except TritonErrorError as exc:
        msg = f"Triton kernel '{kernel_name}' error: {exc}"
        logger.warning(msg)
        warnings.warn(msg, RuntimeWarning)
        if fallback_fn is not None:
            return fallback_fn(*args, **kwargs)
        raise
    return None  # In-place kernels typically return None


def triton_kernel_regime(kernel_name: str) -> dict[str, str]:
    """
    Document the operational regime for a Triton kernel.

    Returns a dict describing when the kernel is expected to work vs fall back.
    This should be added to the kernel's docstring.

    Args:
        kernel_name: Name of the kernel

    Returns:
        Dict with regime description
    """
    regimes = {
        "tile_activity_update": {
            "works": "CUDA device, Triton 2.1+, shapes divisible by BLOCK_B/BLOCK_N",
            "falls_back": "CPU, no Triton, shape not divisible by block size, OOM",
        },
        "tile_prediction": {
            "works": "CUDA device, Triton 2.1+, valid input shapes",
            "falls_back": "CPU, no Triton, OOM",
        },
        "tile_contrastive_update": {
            "works": "CUDA device, Triton 2.1+, valid input shapes",
            "falls_back": "CPU, no Triton, OOM",
        },
        "tile_hebbian_update": {
            "works": "CUDA device, Triton 2.1+, valid input shapes",
            "falls_back": "CPU, no Triton, OOM",
        },
        "hebbian_update": {
            "works": "CUDA device, Triton 2.1+, 2D tileable shapes",
            "falls_back": "CPU, no Triton, non-tileable shapes, OOM",
        },
        "three_factor_hebbian": {
            "works": "CUDA device, Triton 2.1+, 2D tileable shapes",
            "falls_back": "CPU, no Triton, non-tileable shapes, OOM",
        },
        "contrastive_hebbian": {
            "works": "CUDA device, Triton 2.1+, 2D tileable shapes",
            "falls_back": "CPU, no Triton, non-tileable shapes, OOM",
        },
        "eqprop_step": {
            "works": "CUDA device, Triton 2.1+, 1D contiguous tensors",
            "falls_back": "CPU, no Triton, non-contiguous, OOM",
        },
        "ep_settle": {
            "works": "CUDA device, Triton 2.1+, layered MLP shapes",
            "falls_back": "CPU, no Triton, CuPy, OOM",
        },
        "muon_orthogonalize": {
            "works": "CUDA device, Triton 2.1+, square-ish matrices",
            "falls_back": "CPU, no Triton, non-square, CuPy, OOM",
        },
        "lif_step": {
            "works": "CUDA device, Triton 2.1+, valid neuron counts",
            "falls_back": "CPU, no Triton, OOM",
        },
        "stdp_update": {
            "works": "CUDA device, Triton 2.1+, valid spike train shapes",
            "falls_back": "CPU, no Triton, OOM",
        },
        "contrastive_stdp": {
            "works": "CUDA device, Triton 2.1+, valid spike train shapes",
            "falls_back": "CPU, no Triton, OOM",
        },
        "ns5_gram": {
            "works": "CUDA device, Triton 2.1+, M>=16, N>=16",
            "falls_back": "CPU, no Triton, small shapes, OOM",
        },
        "ns5_square": {
            "works": "CUDA device, Triton 2.1+, N>=16",
            "falls_back": "CPU, no Triton, small shapes, OOM",
        },
        "ns5_update": {
            "works": "CUDA device, Triton 2.1+, M>=16, N>=16",
            "falls_back": "CPU, no Triton, small shapes, OOM",
        },
    }
    return regimes.get(
        kernel_name,
        {
            "works": "CUDA device, Triton available, valid shapes",
            "falls_back": "CPU, no Triton, OOM, shape mismatch",
        },
    )


__all__ = ["safe_triton_launch", "triton_kernel_regime"]
