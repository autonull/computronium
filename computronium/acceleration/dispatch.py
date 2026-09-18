"""Backend Dispatch Policy.

Selects a backend safely based on implementation spec and requested backend.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from computronium.acceleration.spec import ImplementationSpec


def select_backend(spec: ImplementationSpec, requested: str = "auto") -> str:
    """Select backend for an implementation.

    Args:
        spec: Implementation specification
        requested: "auto", "reference", or "kernel"

    Returns:
        Selected backend name ("reference" or "kernel")

    Raises:
        ValueError: If requested backend is not supported
    """
    if requested == "reference":
        return "reference"

    if requested == "kernel":
        if "kernel" not in spec.supported_backends:
            raise ValueError(f"no kernel backend for {spec.id}")
        return "kernel"

    if requested == "auto":
        if "kernel" in spec.supported_backends and spec.status in {
            "kernel_verified",
            "microbenched",
            "campaign_ready",
        }:
            return "kernel"
        return "reference"

    raise ValueError(f"unknown backend request: {requested}")
