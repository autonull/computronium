"""Paper registry: the single-source record of paper status and evidence.

Mirrors the demo-gallery discipline (TODO17 §3.1): every claim in an
``active_draft`` paper must resolve to an existing artifact — a figure
run record, a log containing the cited number, or a data table. The
claim lock (``tests/integration/test_paper_claims.py``) fails any claim
without backing evidence.

Paper status vocabulary (TODO17 §2):

- ``active_draft``: claims stable, evidence complete, writing in progress
- ``parked``: evidence complete, no viable headline; awaiting a new
  result or a fold decision
- ``blocked``: a claim depends on an open cell
- ``published``: shipped; claims frozen against the release commit
- ``retracted``: a core claim was overturned; preserved as record
"""

from __future__ import annotations

from typing import Literal

PaperStatus = Literal["active_draft", "parked", "blocked", "published", "retracted"]

FOLDS: dict[str, str] = {
    "p_axis_boundaries": (
        "icu_law — folds in as the 'plasticity does not modulate the "
        "credit×update surface' negative-result section; no positive "
        "headline of its own (TODO16 §7.1 verdict, recorded 2026-09-10)."
    ),
}

PAPERS: dict[str, dict] = {
    "icu_law": {
        "title": (
            "The Geometry of Local Credit: How Optimizer Displacement "
            "Dictates Learnability"
        ),
        "status": "active_draft",
        "claim_tiers": ["Tier D"],
        "evidence": {
            "figures": ["d19_depth_harvest", "d2_swap_credit"],
            "run_records": ["logs/w1_credit_ladder.log", "data/icu_measurements.csv"],
            "held_out_validation": 0.944,
        },
        "gaps": [],
    },
    "p_axis_expressiveness": {
        "title": (
            "Plasticity as Computation: Unfolding Kolmogorov Complexity "
            "on a Fixed Substrate"
        ),
        "status": "active_draft",
        "claim_tiers": ["E2", "E3", "E4"],  # E1 falsified (TODO17 §Phase B)
        "evidence": {
            "run_records": [
                "logs/w17_e2.log",
                "logs/w17_e3.log",
                "logs/w17_e3_seed0.log",
                "logs/w17_e3_seed1.log",
                "logs/w17_e3_seed2.log",
                "logs/w17_e4.log",
            ],
        },
        "gaps": [
            "headline writing in progress",
            "E1 boundary: composition-error compounding on chaotic "
            "unfolding, sharpened by E1b (credit horizon) and E1c "
            "(operator-space fit: linear ~N·ε² accumulation, "
            "chunking-invariant) into a precision-scaling law — "
            "ε² ≲ MSE_budget/N (TODO17 progress block)",
            "E3 stability budget: cross-pattern rules require "
            "σ_max(J_F) ∈ [1.4, 2.8]; 6/8 patterns are stable "
            "attractors (TODO17 session 5)",
        ],
    },
    "p_axis_boundaries": {
        "title": "What Frozen Weights Can and Cannot Do",
        "status": "parked",
        "claim_tiers": ["L2/L3 benchmarks", "Z3 toy", "campaign 7.1"],
        "evidence": {"figures": ["d17_multi_psi_swap"]},
        "gaps": [],
        "folded_into": "icu_law",
    },
}
