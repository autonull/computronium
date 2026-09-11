"""Preset registry — one-line composition over existing factories only.

No new ontology semantics: each preset wraps an existing validated
construction path (`computronium.core.presets` factories or the extracted
mechanism packages). Mechanism presets are descriptors that delegate to
`computronium_lab.recipes`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from computronium.core.presets import (
    create_backprop_mlp,
    create_eqprop_mlp,
    create_fa_mlp,
    create_ff_mlp,
    create_pepita_mlp,
)

if TYPE_CHECKING:
    from collections.abc import Callable

QUICK_DIMS = {"input_dim": 32, "hidden_dims": (64, 32), "output_dim": 4}


@dataclass(frozen=True, slots=True)
class Preset:
    """A named, one-line system/mechanism constructor."""

    name: str
    kind: str  # "system" | "mechanism"
    summary: str
    build_system: Callable[..., object] | None = None
    recipe_name: str | None = None
    defaults: dict[str, object] = field(default_factory=dict)


def _role_split_builder(**kwargs: object) -> object:
    """Lazy builder: the role-split system is constructed by the recipes
    layer (which derives the readout param name from the geometry)."""
    from computronium_lab.recipes import build_role_split_muon_readout

    return build_role_split_muon_readout(**kwargs)  # type: ignore[arg-type]


PRESETS: dict[str, Preset] = {
    p.name: p
    for p in (
        Preset(
            name="backprop_mlp",
            kind="system",
            summary="Standard backprop MLP (5-D coordinate).",
            build_system=create_backprop_mlp,
        ),
        Preset(
            name="eqprop_mlp",
            kind="system",
            summary="Equilibrium-Propagation MLP (energy-minimization settling).",
            build_system=create_eqprop_mlp,
            defaults={
                "beta": 0.5,
                "inference_steps": 20,
                "hidden_dims": (64, 64, 64),
            },
        ),
        Preset(
            name="fa_mlp",
            kind="system",
            summary="Feedback-Alignment MLP (fixed random feedback credit).",
            build_system=create_fa_mlp,
            # quick-tuned: the internal default lr=0.001 is too weak to make
            # progress on the quick task inside a few epochs
            defaults={"lr": 0.05},
        ),
        Preset(
            name="ff_mlp",
            kind="system",
            summary="Forward-Forward MLP (local goodness credit).",
            build_system=create_ff_mlp,
        ),
        Preset(
            name="pepita_mlp",
            kind="system",
            summary="PEPITA MLP (input-modulated error feedback).",
            build_system=create_pepita_mlp,
        ),
        Preset(
            name="temporal_psi_task_switcher",
            kind="mechanism",
            summary="Frozen-backbone task switching via temporal-ψ ridge readout "
            "(packages/psi-peft; X-TPC-001..003).",
            recipe_name="temporal_psi",
        ),
        Preset(
            name="adaptive_local_feedback",
            kind="mechanism",
            summary="Adaptive local feedback for local credit "
            "(packages/local-feedback; X-ALI-001/002).",
            recipe_name="adaptive_feedback",
        ),
        Preset(
            name="role_split_muon_readout",
            kind="system",
            summary="Role-split update: muon-class orthogonalization on the "
            "readout, euclidean elsewhere (X-USU-001 winner).",
            build_system=_role_split_builder,
            recipe_name="role_split_muon_readout",
        ),
    )
}

ONTOLOGY_PRESET_NAMES = sorted(
    p.name for p in PRESETS.values() if p.kind == "system" and p.build_system
)


def build_system_preset(name: str, **kwargs: object) -> object:
    """Compose a System from a registered ontology preset."""
    preset = PRESETS.get(name)
    if preset is None or preset.build_system is None:
        known = ", ".join(ONTOLOGY_PRESET_NAMES)
        raise ValueError(
            f"unknown or non-system preset {name!r}; system presets: {known}"
        )
    merged: dict[str, object] = {**QUICK_DIMS, **preset.defaults, **kwargs}
    return preset.build_system(**merged)  # type: ignore[arg-type]
