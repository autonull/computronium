"""Reference implementation for Complex Substrate.

Delegates to computronium.ontology.substrate._substrate.ComplexSubstrate (the source of truth).
This wrapper provides the uniform `make_substrate(spec)` factory interface.
"""

from computronium.ontology.substrate._substrate import ComplexSubstrate, SubstrateConfig
from computronium.ontology.substrate.spec import (
    SubstrateSpec,
)


def make_substrate(spec: SubstrateSpec):
    """Create a complex substrate instance from a SubstrateSpec."""
    config = SubstrateConfig.complex(
        noise_level=spec.noise_model.level,
        weight_bounds=spec.structural_constraints.weight_bounds,
        sparsity=spec.structural_constraints.sparsity,
        device="cpu",
    )
    return ComplexSubstrate(config)
