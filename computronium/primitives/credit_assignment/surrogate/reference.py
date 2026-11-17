"""Reference implementation for the straight-through surrogate credit.

Delegates to :class:`SurrogateCredit` (the source of truth). This wrapper
provides the uniform ``step(case)`` interface for parity/microbench.
"""

from typing import Any

from computronium.ontology.credit import (
    CreditAssignmentConfig,
    SurrogateCredit,
)
from computronium.primitives._common import make_estimator_reference_step


def _config_factory(config: dict[str, Any]) -> CreditAssignmentConfig:
    return CreditAssignmentConfig.surrogate()


step = make_estimator_reference_step(SurrogateCredit, _config_factory)
