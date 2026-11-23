#!/usr/bin/env python
"""Run capability tests for specific primitives.

Usage:
    uv run python scripts/run_capability.py --primitives substrate_coupled,rule_state
    uv run python scripts/run_capability.py --session A
    uv run python scripts/run_capability.py --all

Sessions:
    A: plasticity fixes (substrate_coupled, rule_state, conflict_adaptive, temporal_psi, closed_form_ridge, routing, fast_weights, null)
    B: update + credits (bayesian_online, elastic_consolidation, local_goodness, thermodynamic_contrast, target_inversion, pc_alm, ...)
    C: geometry + dynamics (graph, recurrent, conv, nca, tile, ntm, attention, causal_transformer, ...)
    D: substrate (ternary, analog, memristive, neuromorphic, quantum, photonic, ...)
"""

from __future__ import annotations

import argparse
import subprocess
import sys

SESSION_PRIMITIVES = {
    "A": [
        "substrate_coupled",
        "rule_state",
        "conflict_adaptive",
        "temporal_psi",
        "closed_form_ridge",
        "routing",
        "fast_weights",
        "null",
    ],
    "B": [
        "bayesian_online",
        "elastic_consolidation",
        "local_goodness",
        "thermodynamic_contrast",
        "target_inversion",
        "pc_alm",
        "random_projections",
        "gradient",
        "local_contrastive",
        "hybrid",
        "forward_tangent",
        "score_function",
        "surrogate",
        "local_supervision",
        "eligibility_prop",
        "unbiased_rtrl",
        "rtrl_reference",
        "zeroth_order",
        "homeostatic",
        "temporal_trace",
        "pepita",
    ],
    "C": [
        "graph",
        "recurrent",
        "conv",
        "nca",
        "tile",
        "tile_mesh",
        "ntm",
        "attention",
        "spatial_lattice",
        "routing",
        "causal_transformer",
        "feedforward",
        "instantaneous",
        "energy_minimization",
        "predictive_settling",
        "error_predictive_coding",
        "pc_alm",
        "diffusion",
        "lazy",
        "spike_integration",
    ],
    "D": [
        "ternary",
        "analog",
        "memristive",
        "neuromorphic",
        "quantum",
        "photonic",
        "complex",
        "optical",
        "sparse",
        "noisy",
        "digital",
    ],
}


def build_k_expression(primitives: list[str]) -> str:
    """Build a pytest -k expression from primitive names."""
    return " or ".join(primitives)


def run_capability(primitives: list[str], extra_args: list[str]) -> int:
    """Run capability tests for the given primitives."""
    k_expr = build_k_expression(primitives)
    cmd = [
        "uv",
        "run",
        "python",
        "-m",
        "pytest",
        "tests/primitives/test_primitive_capability.py",
        "-k",
        k_expr,
        "-q",
        *extra_args,
    ]
    print(f"Running: {' '.join(cmd)}", file=sys.stderr)
    result = subprocess.run(cmd)
    return result.returncode


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument(
        "--primitives",
        help="Comma-separated list of primitive names (short names, e.g. substrate_coupled)",
    )
    parser.add_argument(
        "--session",
        choices=["A", "B", "C", "D", "all"],
        help="Run capability for a predefined session group",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Run capability for all primitives",
    )
    parser.add_argument(
        "extra_args",
        nargs=argparse.REMAINDER,
        help="Extra arguments passed to pytest (use -- to separate)",
    )
    # Parse known args only, leave unknown for pytest
    args, unknown = parser.parse_known_args(argv)
    args.extra_args = unknown

    if args.all:
        primitives = [p for group in SESSION_PRIMITIVES.values() for p in group]
        # Deduplicate while preserving order
        seen = set()
        primitives = [p for p in primitives if not (p in seen or seen.add(p))]
    elif args.session:
        primitives = SESSION_PRIMITIVES[args.session]
    elif args.primitives:
        primitives = [p.strip() for p in args.primitives.split(",")]
    else:
        parser.error("One of --primitives, --session, or --all is required")

    return run_capability(primitives, args.extra_args)


if __name__ == "__main__":
    raise SystemExit(main())
