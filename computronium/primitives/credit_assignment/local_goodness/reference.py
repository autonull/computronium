"""Reference implementation for Local Goodness Credit Assignment.

Delegates to computronium.ontology.credit.LocalGoodnessCredit (the source of truth).
This wrapper provides the uniform `step(case)` interface for parity/microbench.
"""

from typing import Any

from computronium.ontology.credit import (
    CreditAssignmentConfig,
    LocalGoodnessCredit,
)
from computronium.primitives._common import make_reference_step


def _config_factory(config: dict[str, Any]) -> CreditAssignmentConfig:
    return CreditAssignmentConfig.local_goodness(
        local_objective=config.get("local_objective", "ff"),
        feedback_scale=config.get("feedback_scale", 1.0),
        orthogonal_init=config.get("orthogonal_init", True),
        readout_error=config.get("readout_error", False),
        credit_norm=config.get("credit_norm", "rms"),
        learned_feedback=config.get("learned_feedback", False),
        feedback_lr=config.get("feedback_lr", 0.01),
        feedback_update_every=config.get("feedback_update_every", 10),
    )


step = make_reference_step(LocalGoodnessCredit, _config_factory)
