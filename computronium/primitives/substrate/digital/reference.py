"""Reference implementation for Digital Substrate.

Delegates to computronium.ontology.substrate.spec.make_substrate (the source of truth).
This wrapper provides the uniform `make_substrate(spec)` factory interface.
"""

from computronium.ontology.substrate.spec import (
    SubstrateSpec,
)
from computronium.ontology.substrate.spec import (
    make_substrate as ontology_make_substrate,
)


def make_substrate(spec: SubstrateSpec):
    """Create a digital substrate instance from a SubstrateSpec.

    This is a thin wrapper around the ontology's make_substrate that
    ensures the substrate type is digital.
    """
    # Ensure digital device model
    if spec.device_model.value != "digital":
        from computronium.ontology.substrate.spec import DeviceModel

        spec = spec.__class__(
            execution_model=spec.execution_model,
            device_model=DeviceModel.DIGITAL,
            numeric_representation=spec.numeric_representation,
            noise_model=spec.noise_model,
            structural_constraints=spec.structural_constraints,
            cost_model=spec.cost_model,
            substrate_type=spec.substrate_type,
        )

    return ontology_make_substrate(spec)
