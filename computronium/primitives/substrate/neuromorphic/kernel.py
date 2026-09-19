"""Accelerated kernel for Neuromorphic Substrate.

Delegates to computronium.ontology.substrate.spec.make_substrate.
Provides uniform `make_substrate(spec)` factory interface.
"""

from computronium.acceleration.backends import kernel_available

KERNEL_TECHNOLOGY = "triton"


def is_available() -> bool:
    return kernel_available(KERNEL_TECHNOLOGY)


def make_substrate(spec):
    """Create a neuromorphic substrate instance from a SubstrateSpec."""
    if not is_available():
        from .reference import make_substrate as reference_make_substrate

        return reference_make_substrate(spec)

    # TODO: Implement accelerated neuromorphic substrate
    from .reference import make_substrate as reference_make_substrate

    return reference_make_substrate(spec)
