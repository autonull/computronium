"""Preset registry semantics."""

from __future__ import annotations

import pytest
from computronium_lab.presets import (
    ONTOLOGY_PRESET_NAMES,
    PRESETS,
    build_system_preset,
)


def test_registry_names_and_kinds() -> None:
    assert set(PRESETS) >= {
        "backprop_mlp",
        "eqprop_mlp",
        "fa_mlp",
        "ff_mlp",
        "pepita_mlp",
        "role_split_muon_readout",
    }
    assert PRESETS["backprop_mlp"].kind == "system"
    assert PRESETS["temporal_psi_task_switcher"].kind == "mechanism"


def test_every_system_preset_has_builder() -> None:
    for name in ONTOLOGY_PRESET_NAMES:
        assert PRESETS[name].build_system is not None


def test_unknown_system_preset_raises() -> None:
    with pytest.raises(ValueError, match="system presets"):
        build_system_preset("temporal_psi_task_switcher")


def test_kwargs_override_quick_dims() -> None:
    system = build_system_preset("backprop_mlp", input_dim=16, output_dim=2)
    params = getattr(system, "geometry").params
    assert params["0.weight"].shape[1] == 16
    assert params["4.weight"].shape[0] == 2
