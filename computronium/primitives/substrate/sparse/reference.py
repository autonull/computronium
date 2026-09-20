"""Reference implementation for Sparse Substrate.

Delegates to computronium.ontology.substrate._substrate.SparseSubstrate (the source of truth).
This wrapper provides the uniform `make_substrate(spec)` factory interface.
"""

from computronium.ontology.substrate._substrate import (
    SparseSubstrate,
    SubstrateConfig,
    SubstrateType,
)
from computronium.ontology.substrate.spec import (
    SubstrateSpec,
)


def make_substrate(spec: SubstrateSpec):
    """Create a sparse substrate instance from a SubstrateSpec."""
    config = SubstrateConfig(
        substrate_type=SubstrateType.SPARSE,
        precision="float32",
        noise_level=spec.noise_model.level,
        weight_bounds=spec.structural_constraints.weight_bounds,
        sparsity=spec.structural_constraints.sparsity,
        device="cpu",
    )
    return SparseSubstrate(config)
