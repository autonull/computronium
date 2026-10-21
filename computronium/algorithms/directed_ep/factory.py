"""Public factory for DirectedEp systems."""

from computronium.acceleration.dispatch import make_factory
from computronium.core.presets import create_directed_ep_mlp as _create_directed_ep_mlp

create_directed_ep_mlp = make_factory(
    _create_directed_ep_mlp,
    "algorithm.directed_ep",
    extra_params=(),
)
