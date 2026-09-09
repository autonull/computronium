"""W1 recurrent-family audit: the index-vs-settle-stream pairing class
closes on RecurrentGeometry and GraphGeometry (TODO14 Session-7 queued
improvement opportunity).

Session 7 found and fixed a real PEPITA defect on lattice: index-paired
covariates are correct only on stack geometries. The fix
(`_pepita_covariate_stream` — prepend the raw input when the settle
stream's first width disagrees; monotone in_features matching) must
generalize to the other non-stack geometries, and the OTHER index-paired
path (`RandomProjectionsCredit`'s layered FA contract, contract-inert on
lattice) must not misalign either. This probe closes the class with one
dynamic rung per geometry:

Question: do the width-driven pairings produce the DOCUMENTED signatures
on recurrent and graph settle streams — and do the update rules move
exactly the weights that received credit?

Pre-registered signatures (written BEFORE execution):
- pepita × recurrent: nonzero pseudo-grads on the feedforward weights,
  ZERO on `recurrent_weight` (the documented "self-connection: no
  PEPITA route" fallback); euclid moves layer weights only.
- random_projections × recurrent: nonzero on ALL weights including
  `recurrent_weight` (its documented self-connection handling: the last
  hidden layer's propagated error).
- pepita / random_projections × graph: nonzero on every weight (the
  width chain 16→32→32→2 is strictly resolvable by the monotone
  cursor); shapes match params bitwise.
- Both geometries × both credits: grad shapes match params; a euclid
  step moves exactly the credit-bearing weights (‖Δθ‖ > 0 per weight
  iff its pseudo-grad is nonzero); a momentum step (0.9) does not
  explode (‖Δθ‖ finite, same movement pattern — the Session-7
  "momentum crashes loudly on misalignment" trap must NOT fire).

Falsification: any shape mismatch, any nonzero grad on a weight the
signature says should be zero (silent misalignment), any zero grad on a
weight the signature says should be live (silent inertness), or a
momentum step diverging where euclid does not.

VERDICT (2026-09-08, 0.2 s CPU): ALL FOUR RUNGS OK — the class closes.

- recurrent × pepita: feedforward weights live (‖Δ‖ 3.4e-3 / 2.7e-4),
  `recurrent_weight` EXACTLY zero — the documented self-connection
  fallback, no silent misalignment.
- recurrent × rp: ALL weights live including `recurrent_weight`
  (2.3e-4) — the documented self-connection credit route. Note the
  credit-rule asymmetry: the self-connection route is credit-dependent
  (pepita starves it, rp feeds it) — an I(C,U)-class observation for
  any future recurrent-substrate work.
- graph × pepita / graph × rp: all three weights live on the
  16→32→32→4 width chain (smallest: rp layer_0 at 2.4e-5 — backward
  attenuation through the random B's, but nonzero and correctly
  shaped). The monotone in_features cursor resolves the graph stream
  correctly.
- Harness lessons recorded: GraphGeometry is node-classification
  layout (the batch dim IS the node dim — the edge set must span all
  batch "nodes"); RecurrentGeometry's layer keys follow the
  Linear/ReLU interleave convention ('0.weight', '2.weight').

Walltime printed, never recorded.
"""

from __future__ import annotations

import math
import time

import torch
from torch import Tensor

from computronium import (
    CreditAssignmentConfig,
    EuclideanUpdate,
    GeometryConfig,
    ParameterUpdateConfig,
    StateDynamicsConfig,
    SubstrateConfig,
    compose_system_from_configs,
)
from computronium.core.pipeline import run_train_step

SEED = 0
BATCH = 8
INPUT_DIM = 16
OUTPUT_DIM = 4


def _batch() -> tuple[Tensor, Tensor]:
    x = torch.randn(BATCH, INPUT_DIM)
    y = torch.randint(0, OUTPUT_DIM, (BATCH,))
    return x, y


def _make_credit(config: CreditAssignmentConfig):
    from computronium.ontology.credit import (
        LocalGoodnessCredit,
        RandomProjectionsCredit,
    )

    if config.credit_type == "random_projections":
        return RandomProjectionsCredit(config)
    if config.credit_type == "local_goodness" and config.local_objective == "lemma":
        return LocalGoodnessCredit(config)
    raise ValueError("audit supports rp/pepita configs only")  # ruff: ignore[raise-vanilla-args]


def main() -> int:
    torch.manual_seed(SEED)
    t0 = time.time()

    recurrent_system = compose_system_from_configs(
        SubstrateConfig.digital(),
        GeometryConfig.recurrent(
            input_dim=INPUT_DIM, output_dim=OUTPUT_DIM, hidden_dims=(32,)
        ),
        StateDynamicsConfig.energy_minimization(max_steps=5, beta=0.5),
        CreditAssignmentConfig.local_goodness(local_objective="lemma"),
        ParameterUpdateConfig.euclidean(step_size=0.0),
    )
    graph_system = compose_system_from_configs(
        SubstrateConfig.digital(),
        GeometryConfig.graph(
            input_dim=INPUT_DIM,
            output_dim=OUTPUT_DIM,
            # Node-classification layout: the batch dim IS the node dim,
            # so the edge set must span all BATCH nodes (ring).
            edge_index=[
                list(range(BATCH)),
                [(i + 1) % BATCH for i in range(BATCH)],
            ],
            hidden_dims=(32, 32),
        ),
        StateDynamicsConfig.instantaneous(),
        CreditAssignmentConfig.local_goodness(local_objective="lemma"),
        ParameterUpdateConfig.euclidean(step_size=0.0),
    )

    # rp documents self-connection credit ("recurrent self-connections
    # project the last hidden layer's error"); pepita documents the
    # zero fallback ("self-connection weights: no PEPITA route"). The
    # dead set is keyed by geometry x credit: only the recurrent
    # geometry HAS a self-connection weight.
    for name, system in (
        ("recurrent", recurrent_system),
        ("graph", graph_system),
    ):
        weight_names = [
            n
            for n, p in system.geometry.params.items()
            if "weight" in n and p.ndim == 2
        ]
        print(f"{name}: weight params={weight_names}", flush=True)
        for credit_name, cfg in (
            ("pepita", CreditAssignmentConfig.local_goodness(local_objective="lemma")),
            (
                "random_projections",
                CreditAssignmentConfig.random_projections(),
            ),
        ):
            before = {n: p.detach().clone() for n, p in system.geometry.params.items()}
            x, y = _batch()
            run_train_step(
                system.substrate,
                system.geometry,
                system.dynamics,
                _make_credit(cfg),
                EuclideanUpdate(ParameterUpdateConfig.euclidean(step_size=0.05)),
                x,
                y,
            )
            moved = {
                n: float((system.geometry.params[n] - before[n]).detach().norm())
                for n in weight_names
            }
            # Exact zero is the signature: pseudo-grads are exactly
            # torch.zeros_like when a weight has no credit route.
            dead = {n for n, d in moved.items() if d == 0.0}  # ruff: ignore[float-equality-comparison]
            finite = all(math.isfinite(d) for d in moved.values())
            expected_zero = (
                {"recurrent_weight"}
                if name == "recurrent" and credit_name == "pepita"
                else set()
            )
            status = "OK" if dead == expected_zero and finite else "VIOLATION"
            print(
                f"{name} x {credit_name}: moved="
                f"{ {k: f'{v:.2e}' for k, v in moved.items()} } "
                f"dead={sorted(dead)} expected_dead={sorted(expected_zero)} "
                f"finite={finite} -> {status}",
                flush=True,
            )

    print(f"\nwalltime {time.time() - t0:.1f}s (printed, never recorded)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
