"""Reference implementation for the score-function estimator.

Delegates to :class:`ScoreFunctionCredit` (the source of truth). This
wrapper provides the uniform ``step(case)`` interface for parity/microbench.
"""

from typing import Any

from computronium.ontology.credit import (
    CreditAssignmentConfig,
    ScoreFunctionCredit,
)
from computronium.primitives._common import make_estimator_reference_step


def _config_factory(config: dict[str, Any]) -> CreditAssignmentConfig:
    return CreditAssignmentConfig.score_function(
        estimator_samples=config.get("estimator_samples", 32),
    )


step = make_estimator_reference_step(ScoreFunctionCredit, _config_factory)
