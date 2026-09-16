"""Credit-channel BP-cosine audit for the G1 atlas families (TODO27 rev 10).

Question: does any measured family's credit signal leak backprop gradients?
A high BP cosine (> ~0.9, the GradientCredit identity-card gate) on a family
that claims local credit would mean the atlas's family ranking is measuring
BP, not the family — an implementation bug, not a discovery.

Audits the families that actually produced the G1 cell data:
- predictive_settling x thermodynamic_contrast / local_contrastive
- energy_minimization x thermodynamic_contrast / local_contrastive
against the same batch, same seed, feedforward geometry (the only topology
credit_trace's BP reference is defined on).

Interpretation bands: cos >= 0.9 => BP leakage (bug); 0.3-0.9 => partially
gradient-aligned (expected for prediction-driven local families, report the
value); < 0.3 => genuinely non-gradient-aligned local credit.

Run: uv run python scripts/probes/credit_channel_audit.py
Walltime: < 1 min (CPU, tiny systems).
"""

from __future__ import annotations

import json
import pathlib

import torch

from computronium.analysis.instruments import credit_trace
from computronium.autoscientist.compose import compose_cell_system

__all__ = ["main"]

AUDIT_CELLS = (
    ("predictive_settling", "thermodynamic_contrast", "adam"),
    ("predictive_settling", "local_contrastive", "adam"),
    ("energy_minimization", "thermodynamic_contrast", "adam"),
    ("energy_minimization", "local_contrastive", "adam"),
)


def main() -> None:
    torch.manual_seed(0)
    x = torch.randn(32, 20)
    y = torch.randint(0, 5, (32,))
    report: dict[str, dict[str, object]] = {
        "cells": {},
        "note": "cos >= 0.9 => BP leakage",
    }  # type: ignore[assignment]

    for dynamics, credit, update in AUDIT_CELLS:
        system = compose_cell_system(
            dynamics=dynamics,
            credit=credit,
            update=update,
            geometry={"topology_type": "feedforward", "depth": 3, "hidden_dim": 32},
            input_dim=20,
            output_dim=5,
        )
        trace = credit_trace(system, x, y, bp_reference=True)
        bp = trace.get("bp_cosine")
        cos = {k: round(v, 4) for k, v in bp.items()} if isinstance(bp, dict) else {}
        min_cos = trace.get("bp_min_cosine")
        norms = trace.get("layer_norms")
        report["cells"][f"{dynamics}|{credit}"] = {
            "bp_cosine": cos,
            "bp_min_cosine": min_cos,
            "layer_norms_sample": dict(list(norms.items())[:3])
            if isinstance(norms, dict)
            else {},
        }
        print(f"{dynamics}|{credit}: bp_cosine={cos}")

    with pathlib.Path("artifacts/credit_channel_audit.json").open("w") as fh:
        json.dump(report, fh, indent=2)
    print("written: artifacts/credit_channel_audit.json")


if __name__ == "__main__":
    main()
