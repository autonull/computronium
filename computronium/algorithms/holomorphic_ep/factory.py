"""Public factory for HolomorphicEp systems."""

from computronium.acceleration.dispatch import make_factory
from computronium.core.presets import (
    create_holomorphic_ep_mlp as _create_holomorphic_ep_mlp,
)

create_holomorphic_ep_mlp = make_factory(
    _create_holomorphic_ep_mlp,
    "algorithm.holomorphic_ep",
    extra_params=(),
)
