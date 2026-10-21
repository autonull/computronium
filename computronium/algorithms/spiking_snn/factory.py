"""Public factory for Spiking SNN systems."""

from computronium.acceleration.dispatch import make_factory
from computronium.core.presets import create_spiking_snn_mlp as _create_spiking_snn_mlp

create_spiking_snn_mlp = make_factory(
    _create_spiking_snn_mlp,
    "algorithm.spiking_snn",
    extra_params=("max_steps", "beta", "threshold"),
)
