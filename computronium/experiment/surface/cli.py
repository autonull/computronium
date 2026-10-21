"""Surface CLI dispatcher with run profiles (WP7).

Single dispatcher replacing legacy entry points. Run profiles as data:
- quick-verify: Fast sanity check (L0/L1, few seeds)
- production-map: Full broad mapping (L0→L1→L2 maturation)
- maturation: Re-run front cells at higher fidelity
- claim: Claim-grade L2 re-runs with CEEC governance

The command implementations live in the ``_cli`` subpackage, one module per
family of commands. This module owns the dispatch table and re-exports the
names the rest of the repo imports from here.
"""

from __future__ import annotations

import json
import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence

from computronium.experiment.execution.policy import (
    create_policy,
    policy_context,
)

from ._cli._analysis import (
    _cmd_axis_attribution,
    _cmd_counterfactual,
    _cmd_energy_landscape,
    _cmd_hardware_variance,
    _cmd_mediation,
    _cmd_nonnormality,
    _cmd_pareto_advanced,
    _cmd_repro_advanced,
    _cmd_seed_variability,
    _cmd_stability_analysis,
)
from ._cli._campaign import _cmd_baseline, _cmd_campaign, _cmd_coverage, _cmd_loop
from ._cli._commands import (
    _cmd_conformance,
    _cmd_export,
    _cmd_gallery,
    _cmd_import,
    _cmd_report,
    _cmd_run,
    _cmd_status,
)
from ._cli._demo import _cmd_demo
from ._cli._execution import (
    _CELL_WORKERS,
    _consumed,
    _resolve_spec,
    _settle_maturity,
    execute_spec,
    spec_from_profile,
)
from ._cli._parser import _build_parser
from ._cli._profiles import CORE_COMMANDS, RUN_PROFILES, RunProfile
from ._cli._registry import _cmd_dashboard, _cmd_dataset, _cmd_environment, _cmd_quality
from ._cli._repro import _cmd_power_analysis, _cmd_repro
from ._cli._schema import _cmd_schema
from ._cli._science import (
    _cmd_defect,
    _cmd_frozen_theta_psi,
    _cmd_hypothesis_campaign,
    _cmd_stability_plasticity,
)
from ._cli._stats import _cmd_diff, _cmd_pareto, _cmd_stats

__all__ = [
    "CORE_COMMANDS",
    "RUN_PROFILES",
    "_CELL_WORKERS",
    "RunProfile",
    "_build_parser",
    "_cmd_loop",
    "_consumed",
    "_resolve_spec",
    "_settle_maturity",
    "create_policy",
    "execute_spec",
    "main",
    "policy_context",
    "spec_from_profile",
]


def main(argv: Sequence[str] | None = None) -> int:
    """Console-script entry point for surface CLI."""
    import logging

    logging.basicConfig(level=logging.INFO, format="%(message)s", force=True)

    # Ensure registries are seeded for objective lookups
    from computronium.experiment.schema import _ensure_registries_seeded

    _ensure_registries_seeded()

    raw = list(sys.argv[1:] if argv is None else argv)
    if "--help-all" in raw:
        _build_parser(full=True).print_help()
        return 0

    args = _build_parser().parse_args(raw)
    if args.command == "run" and args.profile is None and args.profile_flag:
        args.profile = args.profile_flag
    command_handlers = {
        "run": _cmd_run,
        "demo": _cmd_demo,
        "report": _cmd_report,
        "export": _cmd_export,
        "import": _cmd_import,
        "conformance": _cmd_conformance,
        "status": _cmd_status,
        "gallery": _cmd_gallery,
        "campaign": _cmd_campaign,
        "hypothesis-campaign": _cmd_hypothesis_campaign,
        "stability-plasticity": _cmd_stability_plasticity,
        "frozen-theta-psi": _cmd_frozen_theta_psi,
        "stats": _cmd_stats,
        "pareto": _cmd_pareto,
        "diff": _cmd_diff,
        "repro": _cmd_repro,
        "schema": _cmd_schema,
        "power-analysis": _cmd_power_analysis,
        "stability-analysis": _cmd_stability_analysis,
        "energy-landscape": _cmd_energy_landscape,
        "nonnormality": _cmd_nonnormality,
        "axis-attribution": _cmd_axis_attribution,
        "counterfactual": _cmd_counterfactual,
        "mediation": _cmd_mediation,
        "pareto-advanced": _cmd_pareto_advanced,
        "seed-variability": _cmd_seed_variability,
        "hardware-variance": _cmd_hardware_variance,
        "repro-advanced": _cmd_repro_advanced,
        "dashboard": _cmd_dashboard,
        "dataset": _cmd_dataset,
        "environment": _cmd_environment,
        "quality": _cmd_quality,
        "loop": _cmd_loop,
        "baseline": _cmd_baseline,
        "coverage": _cmd_coverage,
        "defect": _cmd_defect,
    }
    try:
        handler = command_handlers.get(args.command)
        if handler is None:
            return 2
        return handler(args)
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as exc:
        # A refused declaration is the user's input, not an internal fault: a
        # traceback here reads as a crash of the tool rather than of the run.
        print(f"comp {args.command}: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
