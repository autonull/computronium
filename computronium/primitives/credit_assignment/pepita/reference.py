"""Reference implementation for PEPITA Credit Assignment.

Delegates to computronium.ontology.credit.PepitaCredit (the source of truth).
This wrapper provides the uniform `step(case)` interface for parity/microbench.
"""

from typing import Any

from computronium.ontology.credit import (
    CreditAssignmentConfig,
    PepitaCredit,
)
from computronium.primitives._common import make_reference_step


def _config_factory(config: dict[str, Any]) -> CreditAssignmentConfig:
    return CreditAssignmentConfig.pepita(
        gamma=config.get("gamma", 0.05),
        feedback_matrix=config.get("feedback_matrix"),
    )


step = make_reference_step(PepitaCredit, _config_factory)
