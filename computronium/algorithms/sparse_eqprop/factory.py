"""Public factory for SparseEqprop systems."""

from computronium.acceleration.dispatch import make_factory
from computronium.core.presets import (
    create_sparse_eqprop_mlp as _create_sparse_eqprop_mlp,
)

create_sparse_eqprop_mlp = make_factory(
    _create_sparse_eqprop_mlp,
    "algorithm.sparse_eqprop",
    extra_params=(),
)
