"""Reference implementation for the forward-tangent estimator.

Delegates to :class:`ForwardTangentCredit` (the source of truth). This
wrapper provides the uniform ``step(case)`` interface for parity/microbench.
"""

from typing import Any

from computronium.ontology.credit import (
    CreditAssignmentConfig,
    ForwardTangentCredit,
)
from computronium.primitives._common import make_estimator_reference_step


def _config_factory(config: dict[str, Any]) -> CreditAssignmentConfig:
    return CreditAssignmentConfig.forward_tangent(
        estimator_samples=config.get("estimator_samples", 8),
    )


step = make_estimator_reference_step(ForwardTangentCredit, _config_factory)
