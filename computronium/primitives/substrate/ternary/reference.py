"""Reference implementation for Ternary Substrate.

Delegates to computronium.ontology.substrate._substrate.TernarySubstrate (the source of truth).
This wrapper provides the uniform `make_substrate(spec)` factory interface.
"""

from computronium.ontology.substrate._substrate import SubstrateConfig, TernarySubstrate
from computronium.ontology.substrate.spec import (
    SubstrateSpec,
)


def make_substrate(spec: SubstrateSpec):
    """Create a ternary substrate instance from a SubstrateSpec."""
    config = SubstrateConfig.ternary(
        noise_level=spec.noise_model.level,
        weight_bounds=spec.structural_constraints.weight_bounds,
        device="cpu",
    )
    return TernarySubstrate(config)
