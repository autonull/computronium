"""TODO28 immediate-item 1: em/instantaneous anomaly diagnosis.

Last verification sweep measured em max 0.111 and instantaneous 0.242 on
cells that earlier runs had at 0.86–0.94. Prime suspect: the param-budget
rematch shrinks ``hidden_dim`` while ``_ruler_lr`` keeps the width-64
ruler lr — a destabilizing lr for narrow settling cells. This probe reruns
matched em/instantaneous × feedforward cells with and without
``--param-budget`` and diffs accuracy, lr, param_count, settle_horizon,
and the spectral instrument.

Usage::

    nohup uv run python scripts/probes/d28_rematch_lr_probe.py \
        > logs/probe_rematch_lr.log 2>&1 &
"""

from __future__ import annotations

import argparse
import json
import logging
import time
from pathlib import Path
from typing import cast

from computronium.autoscientist.bridge import ExperimentProposal
from computronium.autoscientist.campaign import AutoScientistCampaign
from computronium.autoscientist.proposer import GRID_CREDITS, GRID_UPDATES

logger = logging.getLogger("d28_probe")

FAMILIES = ("energy_minimization", "instantaneous")


def viable_cells(topology: str = "feedforward") -> list[tuple[str, str, str]]:
    """Viable (dynamics, credit, update) triples at the given topology."""
    from computronium.autoscientist.compose import build_geometry_config
    from computronium.ontology import (
        CreditAssignmentConfig,
        DigitalSubstrate,
        ParameterUpdateConfig,
        StateDynamicsConfig,
    )
    from computronium.ontology.system import SystemConfig

    substrate = DigitalSubstrate().config
    geometry = build_geometry_config(
        {"topology_type": topology, "depth": 2, "hidden_dim": 64},
        input_dim=256,
        output_dim=10,
    )
    viable: list[tuple[str, str, str]] = []
    for dynamics in FAMILIES:
        dcfg = getattr(StateDynamicsConfig, dynamics)()
        for credit in GRID_CREDITS:
            ccfg = getattr(CreditAssignmentConfig, credit)()
            for update in GRID_UPDATES:
                try:
                    ucfg = getattr(ParameterUpdateConfig, update)()
                except TypeError:
                    continue
                try:
                    SystemConfig(
                        substrate=substrate,
                        geometry=geometry,
                        dynamics=dcfg,
                        credit=ccfg,
                        update=ucfg,
                    ).validate()
                except ValueError:
                    continue
                viable.append((dynamics, credit, update))
    return viable


def _proposal(
    dynamics: str, credit: str, update: str, budget: int
) -> ExperimentProposal:
    return ExperimentProposal(
        hypothesis=f"rematch probe {dynamics}|{credit}|{update}",
        model="eqprop",
        task="digits",
        geometry={
            "topology_type": "feedforward",
            "depth": 2,
            "hidden_dim": 64,
            "init_scheme": "default",
        },
        dynamics=dynamics,
        credit=credit,
        update=update,
        hyperparams={"epochs": 1, "param_budget": budget},
        justification="TODO28 anomaly diagnosis probe",
        expected_outcome="accuracy with/without param rematch",
        priority=0.5,
        tags=["probe", "d28_rematch_lr"],
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--per-family", type=int, default=5)
    parser.add_argument("--epochs", type=int, default=1)
    parser.add_argument("--budget", type=int, default=25000)
    parser.add_argument(
        "--out", type=Path, default=Path("scripts/probes/data/d28_rematch_lr.json")
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.WARNING)
    cells = viable_cells()
    picked: list[tuple[str, str, str]] = []
    for dynamics in FAMILIES:
        family = [c for c in cells if c[0] == dynamics]
        # Even stride over credits×updates for spread, not depth.
        picked.extend(
            family[:: max(1, len(family) // args.per_family)][: args.per_family]
        )

    campaign = AutoScientistCampaign(
        knowledge_base=None,
        output_dir="artifacts/probe_rematch_lr",
        db_path="artifacts/probe_rematch_lr/campaign.db",
        branch_name="d28_rematch_lr_probe",
    )
    rows: list[dict[str, object]] = []
    for dynamics, credit, update in picked:
        for budget in (args.budget, 0):
            proposal = _proposal(dynamics, credit, update, budget)
            started = time.time()
            try:
                result = campaign._execute_proposal(proposal)  # ruff: ignore[private-member-access]
            except (RuntimeError, ValueError) as exc:
                logger.warning(
                    "cell crashed: %s|%s|%s b=%d: %s",
                    dynamics,
                    credit,
                    update,
                    budget,
                    exc,
                )
                continue
            rows.append({
                "dynamics": dynamics,
                "credit": credit,
                "update": update,
                "param_budget": budget,
                "accuracy": result.get("final_accuracy"),
                "train_accuracy": result.get("train_accuracy"),
                "param_count": result.get("param_count"),
                "lr": result.get("lr"),
                "settle_horizon": result.get("settle_horizon"),
                "spectral_radius": result.get("spectral_radius"),
                "seconds": round(time.time() - started, 1),
            })
            logger.info("%s", rows[-1])

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")

    # Paired diff per cell
    by_cell: dict[tuple[str, str, str], dict[int, float]] = {}
    for row in rows:
        key = cast(
            "tuple[str, str, str]",
            (row["dynamics"], row["credit"], row["update"]),
        )
        budget = cast("int", row["param_budget"])
        by_cell.setdefault(key, {})[budget] = float(
            cast("float | None", row["accuracy"]) or 0.0
        )
    print(f"{'cell':55s} {'budget':>8s} {'none':>8s} {'diff':>8s}")
    for key, accs in by_cell.items():
        a_budget = accs.get(args.budget, float("nan"))
        a_free = accs.get(0, float("nan"))
        print(
            f"{'|'.join(key):55s} {a_budget:8.3f} {a_free:8.3f} {a_budget - a_free:8.3f}"
        )


if __name__ == "__main__":
    main()
