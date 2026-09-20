"""Accelerated kernel for Complex Substrate.

Delegates to computronium.ontology.substrate._substrate.ComplexSubstrate with triton acceleration.
Provides uniform `make_substrate(spec)` factory interface.
"""

from computronium.acceleration.backends import kernel_available
from computronium.ontology.substrate._substrate import ComplexSubstrate, SubstrateConfig
from computronium.ontology.substrate.spec import SubstrateSpec

KERNEL_TECHNOLOGY = "triton"


def is_available() -> bool:
    return kernel_available(KERNEL_TECHNOLOGY)


def make_substrate(spec: SubstrateSpec):
    """Create a complex substrate instance from a SubstrateSpec."""
    if not is_available():
        from .reference import make_substrate as reference_make_substrate

        return reference_make_substrate(spec)

    # Use accelerated implementation (Triton TODO - substrate optimization)
    config = SubstrateConfig.complex(
        noise_level=spec.noise_model.level,
        weight_bounds=spec.structural_constraints.weight_bounds,
        sparsity=spec.structural_constraints.sparsity,
        device="cpu",
    )
    return ComplexSubstrate(config)
