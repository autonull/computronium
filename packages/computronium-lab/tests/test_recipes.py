"""Recipe layer — validated mechanisms resolve and build in scope."""

from __future__ import annotations

import pytest
import torch
from computronium_lab import RECIPES, build_recipe


def test_recipe_registry_minimum() -> None:
    assert {"temporal_psi", "adaptive_feedback", "role_split_muon_readout"} <= set(
        RECIPES
    )


def test_every_recipe_carries_scope_and_evidence() -> None:
    for recipe in RECIPES.values():
        assert recipe.summary and recipe.when_to_use and recipe.when_not
        assert recipe.evidence


def test_build_temporal_psi() -> None:
    readout = build_recipe("temporal_psi", feature_dim=16, num_classes=3)
    h = torch.randn(8, 16)
    y = torch.randint(0, 3, (8,))
    getattr(readout, "update")(h, y)
    assert getattr(readout, "forward")(h).shape == (8, 3)


def test_build_adaptive_feedback() -> None:
    fb = build_recipe("adaptive_feedback", in_features=8, out_features=4)
    w = torch.randn(4, 8)
    getattr(fb, "update")(w)
    assert getattr(fb, "weight").shape == (4, 8)


def test_build_role_split_system() -> None:
    system = build_recipe("role_split_muon_readout")
    metrics = getattr(system, "train_step")(
        torch.randn(8, 32), torch.randint(0, 4, (8,))
    )
    assert metrics["loss"] > 0.0


def test_build_stable_amplification() -> None:
    amp = build_recipe("stable_amplification")
    x = torch.randn(4, 4)
    y = getattr(amp, "__call__")(x)
    assert y.shape == (4, 4)
    assert getattr(amp, "rho") <= 0.95
    assert getattr(amp, "sigma_max") > 1.0


def test_unknown_recipe_raises() -> None:
    with pytest.raises(ValueError, match="unknown recipe"):
        build_recipe("nope")
