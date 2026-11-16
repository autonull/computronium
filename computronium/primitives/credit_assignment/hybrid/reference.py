"""Reference implementation for Hybrid Credit Assignment.

Delegates to computronium.ontology.credit.HybridCredit (the source of truth).
This wrapper provides the uniform `step(case)` interface for parity/microbench.
"""

from typing import Any

from computronium.ontology.credit import (
    CreditAssignmentConfig,
    HybridCredit,
)
from computronium.primitives._common import make_reference_step


def _config_factory(config: dict[str, Any]) -> CreditAssignmentConfig:
    return CreditAssignmentConfig.hybrid(
        split_layer=config.get("split_layer", -1),
        gamma=config.get("gamma", 0.05),
        feedback_matrix=config.get("feedback_matrix"),
    )


step = make_reference_step(HybridCredit, _config_factory)
