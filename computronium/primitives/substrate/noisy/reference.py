"""Reference implementation for Noisy Substrate.

Delegates to computronium.ontology.substrate._substrate.NoisySubstrate (the source of truth).
This wrapper provides the uniform `make_substrate(spec)` factory interface.
"""

# ruff: ignore[typing-only-first-party-import]
from computronium.ontology.substrate._substrate import (
    NoisySubstrate,
    SubstrateConfig,
    SubstrateType,
)
from computronium.ontology.substrate.spec import (
    SubstrateSpec,
)


def make_substrate(spec: SubstrateSpec):
    """Create a noisy substrate instance from a SubstrateSpec.

    This directly uses NoisySubstrate with a SubstrateConfig derived from the spec.
    """
    config = SubstrateConfig(
        substrate_type=SubstrateType.DIGITAL,
        precision="float32",
        noise_level=spec.noise_model.level,
        weight_bounds=spec.structural_constraints.weight_bounds,
        sparsity=spec.structural_constraints.sparsity,
        device="cpu",
    )
    return NoisySubstrate(config)
