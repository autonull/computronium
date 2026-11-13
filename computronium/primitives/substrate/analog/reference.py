"""Reference implementation for Analog Substrate.

Delegates to computronium.ontology.substrate._substrate.AnalogSubstrate (the
source of truth). This wrapper provides the uniform `make_substrate(spec)`
factory interface.
"""

from typing import TYPE_CHECKING

from computronium.ontology.substrate._substrate import AnalogSubstrate, SubstrateConfig

if TYPE_CHECKING:
    from computronium.ontology.substrate.spec import SubstrateSpec


def make_substrate(spec: SubstrateSpec):
    """Create an analog substrate instance from a SubstrateSpec."""
    config = SubstrateConfig.analog(
        noise_level=spec.noise_model.level,
        device="cpu",
    )
    return AnalogSubstrate(config)


# Alias for the registry's uniform entry naming
step = make_substrate
