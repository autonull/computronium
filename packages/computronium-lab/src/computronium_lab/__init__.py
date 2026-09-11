"""computronium_lab — one-line composition, training, comparison, reporting.

High-level API over the Computronium 6-axis ontology. Wraps existing
validated factories only; CEEC evidence recording is optional and off by
default.
"""

from __future__ import annotations

from computronium_lab.lab import ComparisonResult, Lab
from computronium_lab.presets import PRESETS
from computronium_lab.recipes import RECIPES, build_recipe

__all__ = [
    "PRESETS",
    "RECIPES",
    "ComparisonResult",
    "Lab",
    "build_recipe",
]
