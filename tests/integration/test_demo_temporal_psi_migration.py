"""D21 — Temporal-ψ readout migration through the core plasticity config
surface (TODO19 rounds 7–8).

A MNIST backbone (784-64-2, gradient credit) is trained on digit>=5 and
then bitwise-frozen. The ψ laws — instantiated from
``PlasticityConfig.temporal_psi`` / ``.conflict_adaptive`` via the
system-trainer dispatch (the core trainer path, not probe-side wiring) —
adapt the readout on a parity → INVERTED-parity → parity stream:

- temporal (ρ=0.9) migrates between the conflicting mappings;
- closed-form (ρ=1) blends them and collapses on the inverted phase;
- the conflict-adaptive law self-switches ρ (rho_used < 1 exists) with
  no boundaries handed in and matches fixed temporal on every phase.

Demonstrated regime (pinned at HEAD): demo scale (1 seed, 250 backbone
episodes, 60 episodes/phase).
"""

from __future__ import annotations

import torch

from computronium.experiments.joint.temporal_psi_migration import (
    MigrationDemoConfig,
    MigrationTask,
    build_backbone,
    frozen_null_accuracy,
    plasticity_from_config,
    probe_accuracy,
    run_stream,
)
from computronium.state.transitions import PlasticityConfig
from computronium.visualization import figure_spec, lines_panel

PHASES = (0, 1, 0)
ADAPTIVE_FLOOR = 0.75
CLOSED_FORM_COLLAPSE = 0.85
MATCH_MARGIN = 0.05


def test_demo_temporal_psi_migration(emit_run_record) -> None:
    torch.manual_seed(0)
    config = MigrationDemoConfig()
    task = MigrationTask.load(config)
    system, stream = build_backbone(config, task)

    null_floor = frozen_null_accuracy(system, stream, config, 1)
    arms = {
        "temporal_090": PlasticityConfig.temporal_psi(trace_decay=0.9),
        "closed_form": PlasticityConfig.temporal_psi(trace_decay=1.0),
        "adaptive": PlasticityConfig.conflict_adaptive(forget_decay=0.5),
    }
    record: dict = {"null_floor_inverted": null_floor, "phases": list(PHASES)}
    phase_accs: dict[str, list[float]] = {}
    rho: dict[str, list[float]] = {}
    for name, plasticity_config in arms.items():
        law = plasticity_from_config(plasticity_config)
        result = run_stream(system, law, stream, config, PHASES)
        phase_accs[name] = result["phase_accs"]  # type: ignore[assignment]
        rho[name] = result["rho_used"]  # type: ignore[assignment]

    # Temporal migrates: every phase off the null floor (both directions).
    for acc, flip in zip(phase_accs["temporal_090"], PHASES, strict=True):
        assert acc >= ADAPTIVE_FLOOR, "temporal must acquire/migrate every phase"
    # Closed-form collapses on the INVERTED phase (blended statistics).
    assert phase_accs["closed_form"][1] <= CLOSED_FORM_COLLAPSE
    assert phase_accs["closed_form"][1] < phase_accs["temporal_090"][1] - 0.10
    # Conflict-adaptive self-switches (ρ < 1 was used) WITHOUT boundaries,
    # and matches fixed temporal within the margin on every phase.
    assert min(rho["adaptive"]) < 0.99, "adaptive must have forgotten at a flip"
    assert max(rho["adaptive"]) > 0.99, "adaptive must re-accumulate at ρ=1"
    for a, t in zip(phase_accs["adaptive"], phase_accs["temporal_090"], strict=True):
        assert a >= t - MATCH_MARGIN, "adaptive must match hand-tuned temporal"
    record["phase_accs"] = phase_accs
    record["adaptive_rho_range"] = [min(rho["adaptive"]), max(rho["adaptive"])]
    record["mastery_probe"] = probe_accuracy(
        system, plasticity_from_config(arms["temporal_090"]), {}, stream, config, 0
    )

    record["figure"] = figure_spec(
        "D21 — frozen-backbone readout migration via the plasticity config surface",
        lines_panel(
            dict(phase_accs),
            chance=null_floor,
            xlabel="stream phase (parity, inverted, parity)",
            ylabel="probe accuracy",
        ),
        figsize=[7, 4],
    )
    emit_run_record("D21", "temporal_psi_migration", record)
