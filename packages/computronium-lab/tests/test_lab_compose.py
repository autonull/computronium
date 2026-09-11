"""Lab compose — preset registry and one-line composition."""

from __future__ import annotations

import pytest
from computronium_lab import PRESETS, Lab

MINIMUM_PRESETS = {
    "backprop_mlp",
    "eqprop_mlp",
    "fa_mlp",
    "ff_mlp",
    "pepita_mlp",
    "temporal_psi_task_switcher",
    "adaptive_local_feedback",
    "role_split_muon_readout",
}


def test_preset_registry_covers_minimum() -> None:
    assert set(PRESETS) >= MINIMUM_PRESETS


def test_compose_all_system_presets() -> None:
    lab = Lab()
    for name in (
        "backprop_mlp",
        "eqprop_mlp",
        "fa_mlp",
        "ff_mlp",
        "pepita_mlp",
    ):
        system = lab.compose(name)
        assert hasattr(system, "train_step")
        assert hasattr(system, "geometry")


def test_compose_role_split_system() -> None:
    lab = Lab()
    system = lab.compose("role_split_muon_readout")
    assert hasattr(system, "train_step")
    update = getattr(system, "update")
    assert update.config.update_type == "role_split"


def test_compose_unknown_preset_raises() -> None:
    with pytest.raises(ValueError, match="unknown preset"):
        Lab().compose("nope_mlp")


def test_mechanism_preset_points_to_recipe() -> None:
    lab = Lab()
    with pytest.raises(ValueError, match="mechanism recipe"):
        lab.compose("temporal_psi_task_switcher")
