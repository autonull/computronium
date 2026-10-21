"""Public factory for Routing systems (6-D joint)."""

from computronium.acceleration.dispatch import make_factory
from computronium.core.presets import create_routing_mlp as _create_routing_mlp

create_routing_mlp = make_factory(
    _create_routing_mlp,
    "algorithm.routing",
    extra_params=("gate_dim", "gate_init_scale"),
)
