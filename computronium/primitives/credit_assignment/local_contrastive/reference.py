"""Reference implementation for Local Contrastive Credit.

Delegates to computronium.ontology.credit.LocalContrastiveCredit (the source
of truth). This wrapper provides the uniform `step(case)` interface.
"""

from typing import Any

from computronium.ontology.credit import CreditAssignmentConfig, LocalContrastiveCredit
from computronium.primitives._common import make_reference_step


def _config_factory(config: dict[str, Any]) -> CreditAssignmentConfig:
    return CreditAssignmentConfig.local_contrastive(
        label_dim=config["label_dim"],
        ema_beta=config.get("ema_beta", 0.99),
        stream_norm=config.get("stream_norm", True),
        contrast_threshold=config.get("contrast_threshold", 2.0),
        contrast_objective=config.get("contrast_objective", "gate"),
        readout_scale=config.get("readout_scale", 1.0),
        sequential_lr=config.get("sequential_lr", 0.0),
    )


step = make_reference_step(LocalContrastiveCredit, _config_factory)
