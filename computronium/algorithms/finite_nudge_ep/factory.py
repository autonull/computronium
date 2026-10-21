"""Public factory for FiniteNudgeEp systems."""

from computronium.acceleration.dispatch import make_factory
from computronium.core.presets import (
    create_finite_nudge_ep_mlp as _create_finite_nudge_ep_mlp,
)

create_finite_nudge_ep_mlp = make_factory(
    _create_finite_nudge_ep_mlp,
    "algorithm.finite_nudge_ep",
    extra_params=(),
)
