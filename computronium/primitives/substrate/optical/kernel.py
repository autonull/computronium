"""Accelerated kernel for Photonic Substrate.

Delegates to computronium.ontology.substrate.spec.make_substrate with triton acceleration.
Provides uniform `make_substrate(spec)` factory interface.
"""

from computronium.acceleration.backends import kernel_available
from computronium.ontology.substrate.spec import (
    SubstrateSpec,
)
from computronium.ontology.substrate.spec import (
    make_substrate as ontology_make_substrate,
)

KERNEL_TECHNOLOGY = "triton"


def is_available() -> bool:
    return kernel_available(KERNEL_TECHNOLOGY)


def make_substrate(spec: SubstrateSpec):
    """Create a photonic substrate instance from a SubstrateSpec."""
    if not is_available():
        from .reference import make_substrate as reference_make_substrate

        return reference_make_substrate(spec)

    # Use accelerated implementation (Triton TODO - substrate optimization)
    # Ensure photonic device model
    if spec.device_model.value != "photonic":
        from computronium.ontology.substrate.spec import DeviceModel

        spec = spec.__class__(
            execution_model=spec.execution_model,
            device_model=DeviceModel.PHOTONIC,
            numeric_representation=spec.numeric_representation,
            noise_model=spec.noise_model,
            structural_constraints=spec.structural_constraints,
            cost_model=spec.cost_model,
            substrate_type=spec.substrate_type,
        )

    return ontology_make_substrate(spec)
