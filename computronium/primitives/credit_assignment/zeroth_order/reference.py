"""Reference implementation for the zeroth-order estimator.

Delegates to :class:`ZerothOrderCredit` (the source of truth). This
wrapper provides the uniform ``step(case)`` interface for parity/microbench.
"""

from typing import Any

from computronium.ontology.credit import (
    CreditAssignmentConfig,
    ZerothOrderCredit,
)
from computronium.primitives._common import make_estimator_reference_step


def _config_factory(config: dict[str, Any]) -> CreditAssignmentConfig:
    return CreditAssignmentConfig.zeroth_order(
        estimator_samples=config.get("estimator_samples", 8),
        fd_step=config.get("fd_step", 1e-2),
    )


step = make_estimator_reference_step(ZerothOrderCredit, _config_factory)
