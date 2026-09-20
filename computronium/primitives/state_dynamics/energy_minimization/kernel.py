"""Accelerated kernel for Energy Minimization (torch.compile rung).

This rung uses torch.compile on the reference implementation.
Promotion criteria:
- Parity passes within 0.0001 abs / 0.001 rel / 0.999 cosine
- Microbench shows speedup over reference
- spec.status promoted to 'kernel_verified' with evidence attached
"""

from typing import Any

from computronium.acceleration.backends import kernel_available
from computronium.acceleration.compile import compile_model

KERNEL_TECHNOLOGY = "torch_compile"


def is_available() -> bool:
    """Check if torch.compile is available and functional."""
    return kernel_available(KERNEL_TECHNOLOGY)


# Cached compiled step function (using function attribute to avoid global)
def _get_compiled_step_fn():
    """Get or create the compiled step function."""
    if not hasattr(_get_compiled_step_fn, "_compiled_step_fn"):
        # Import reference step
        module_path = ["computronium.primitives.state_dynamics.energy_minimization.reference", "step"][0]
        func_name = ["computronium.primitives.state_dynamics.energy_minimization.reference", "step"][1]
        module = __import__(module_path, fromlist=[func_name])
        reference_step = getattr(module, func_name)

        # Compile the reference step function
        _get_compiled_step_fn._compiled_step_fn = compile_model(reference_step, mode="reduce-overhead")
    return _get_compiled_step_fn._compiled_step_fn


def step(case: Any) -> Any:
    """Execute one accelerated step using torch.compile.

    Args:
        case: Opaque case object from cases.make_case()

    Returns:
        Same output format as reference.step()
    """
    if not is_available():
        # Fallback to reference
        module_path = ["computronium.primitives.state_dynamics.energy_minimization.reference", "step"][0]
        func_name = ["computronium.primitives.state_dynamics.energy_minimization.reference", "step"][1]
        module = __import__(module_path, fromlist=[func_name])
        reference_step = getattr(module, func_name)
        return reference_step(case)

    # Use torch.compile accelerated step
    compiled_step = _get_compiled_step_fn()
    return compiled_step(case)
