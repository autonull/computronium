"""TODO28 immediate-item 3: topology-lr calibration.

``_ruler_lr`` gives non-feedforward topologies a flat 1e-3 — a
topology-lr confound in the broad map. This probe measures one viable
instantaneous cell per topology at lr {1e-2, 1e-3, 1e-4} (1 epoch,
1 seed) to check whether the flat default is leaving accuracy on the
table or destabilizing any topology.

Usage::

    nohup uv run python scripts/probes/d28_topology_lr_probe.py \
        > logs/probe_topology_lr.log 2>&1 &
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
from computronium.autoscientist.proposer import (
    GRID_CREDITS,
    GRID_TOPOLOGIES,
    GRID_UPDATES,
)

logger = logging.getLogger("d28_lr_probe")

LRS = (1e-2, 1e-3, 1e-4)


def first_viable_cell(
    campaign: AutoScientistCampaign, topology: str, epochs: int
) -> tuple[str, str] | None:
    """First (credit, update) that passes validate() AND the dry-run gate.

    validate() alone is insufficient: task-shape crashes (attention
    head-split, ntm 2-D token expectations) pass it but die in the
    executor — exactly what the campaign's dry-run gate exists to catch.
    """
    from computronium.autoscientist.compose import build_geometry_config
    from computronium.ontology import (
        CreditAssignmentConfig,
        DigitalSubstrate,
        ParameterUpdateConfig,
        StateDynamicsConfig,
    )
    from computronium.ontology.system import SystemConfig

    geometry = build_geometry_config(
        {"topology_type": topology, "depth": 2, "hidden_dim": 64},
        input_dim=64,
        output_dim=10,
    )
    for credit in GRID_CREDITS:
        for update in GRID_UPDATES:
            try:
                ucfg = getattr(ParameterUpdateConfig, update)()
            except TypeError:
                continue
            try:
                SystemConfig(
                    substrate=DigitalSubstrate().config,
                    geometry=geometry,
                    dynamics=StateDynamicsConfig.instantaneous(),
                    credit=getattr(CreditAssignmentConfig, credit)(),
                    update=ucfg,
                ).validate()
            except ValueError:
                continue
            proposal = ExperimentProposal(
                hypothesis="dry-run viability probe",
                model="eqprop",
                task="digits",
                geometry={
                    "topology_type": topology,
                    "depth": 2,
                    "hidden_dim": 64,
                    "init_scheme": "default",
                },
                dynamics="instantaneous",
                credit=credit,
                update=update,
                hyperparams={"epochs": epochs, "param_budget": 25000},
                justification="TODO28 topology-lr calibration",
                expected_outcome="lr sensitivity per topology",
                priority=0.5,
                tags=["probe", "d28_topology_lr"],
            )
            try:
                campaign._execute_proposal(proposal, dry_run=True)  # ruff: ignore[private-member-access]
            except (RuntimeError, ValueError, TypeError) as exc:
                logger.warning(
                    "gate reject %s|%s|%s: %s", topology, credit, update, exc
                )
                continue
            return credit, update
    return None


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--epochs", type=int, default=1)
    parser.add_argument(
        "--out", type=Path, default=Path("scripts/probes/data/d28_topology_lr.json")
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.WARNING)
    campaign = AutoScientistCampaign(
        knowledge_base=None,
        output_dir="artifacts/probe_topology_lr",
        db_path="artifacts/probe_topology_lr/campaign.db",
        branch_name="d28_topology_lr_probe",
    )
    rows: list[dict[str, object]] = []
    for topology in GRID_TOPOLOGIES:
        cell = first_viable_cell(campaign, topology, args.epochs)
        if cell is None:
            logger.warning("no viable instantaneous cell at %s", topology)
            continue
        credit, update = cell
        for lr in LRS:
            proposal = ExperimentProposal(
                hypothesis=f"topology-lr calibration {topology} @ {lr}",
                model="eqprop",
                task="digits",
                geometry={
                    "topology_type": topology,
                    "depth": 2,
                    "hidden_dim": 64,
                    "init_scheme": "default",
                },
                dynamics="instantaneous",
                credit=credit,
                update=update,
                hyperparams={"epochs": args.epochs, "lr": lr, "param_budget": 25000},
                justification="TODO28 topology-lr calibration",
                expected_outcome="lr sensitivity per topology",
                priority=0.5,
                tags=["probe", "d28_topology_lr"],
            )
            started = time.time()
            try:
                result = campaign._execute_proposal(proposal)  # ruff: ignore[private-member-access]
            except (RuntimeError, ValueError) as exc:
                logger.warning("%s @ %s crashed: %s", topology, lr, exc)
                continue
            rows.append({
                "topology": topology,
                "credit": credit,
                "update": update,
                "lr": lr,
                "accuracy": result.get("final_accuracy"),
                "settle_horizon": result.get("settle_horizon"),
                "spectral_radius": result.get("spectral_radius"),
                "seconds": round(time.time() - started, 1),
            })
            logger.info("%s", rows[-1])

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")

    print(f"{'topology':18s} {'cell':40s} " + " ".join(f"lr={lr:<9g}" for lr in LRS))
    for topology in GRID_TOPOLOGIES:
        sub = [r for r in rows if r["topology"] == topology]
        if not sub:
            continue
        cell = f"{sub[0]['credit']}|{sub[0]['update']}"
        accs = {
            cast("float", r["lr"]): float(cast("float | None", r["accuracy"]) or 0.0)
            for r in sub
        }
        print(
            f"{topology:18s} {cell:40s} "
            + " ".join(f"{accs.get(lr, float('nan')):<11.3f}" for lr in LRS)
        )


if __name__ == "__main__":
    main()
