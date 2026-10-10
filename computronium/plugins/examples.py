"""Example plugins for testing/documentation."""

from __future__ import annotations

from typing import Any

from computronium.plugins.core.base import BaseObjectivePlugin


class ExampleObjectivePlugin(BaseObjectivePlugin):
    """Example custom objective plugin."""

    name = "example_objective"
    description = "Example objective that computes accuracy - loss"

    def compute(self, payload: dict[str, Any], **kwargs: Any) -> float:
        accuracy = payload.get("accuracy", 0.0)
        loss = payload.get("loss", 1.0)
        return accuracy - loss

    def requires(self) -> list[str]:
        return ["accuracy", "loss"]
