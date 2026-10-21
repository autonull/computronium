"""Public factory for Feedback Alignment systems."""

from computronium.acceleration.dispatch import make_factory
from computronium.core.presets import create_fa_mlp as _create_fa_mlp

create_fa_mlp = make_factory(
    _create_fa_mlp,
    "algorithm.fa",
    extra_params=("feedback_scale",),
)
