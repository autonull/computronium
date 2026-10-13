#!/usr/bin/env python3
"""Continuous experiment controller: propose → run → analyze → update → repeat.

Drives the existing ``run_experiment.py`` machinery in bounded cycles so the
process never depends on a human invoking a run. Each cycle is short enough to
survive a process watchdog; state is checkpointed after every cycle so the
controller is resumable if killed.

The ladder:

* **explore** — broad L0 production-map over the full available space, cheap,
  accumulates the Pareto front.
* **exploit** — L1 run whose axes are restricted to the primitives of the
  cumulative top-K cells, so the search concentrates on what worked.

Every cycle appends a ledger row (durable, human-readable) and rewrites
``state.json``. Re-running the script resumes from the last cycle.

Usage:
    uv run python scripts/continuous_experiment.py --hours 4 --device cuda
    uv run python scripts/continuous_experiment.py --cycles 2 --device cuda  # smoke
"""

from __future__ import annotations

import argparse
import json
import signal
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATE_DIR = ROOT / "experiments" / "continuous"
STATE_FILE = STATE_DIR / "state.json"
LEDGER_FILE = STATE_DIR / "ledger.jsonl"
STORE_FILE = STATE_DIR / "continuous.duckdb"
LOG_DIR = ROOT / "logs"

AXIS_FLAGS = {
    "substrate": "--substrates",
    "geometry": "--geometries",
    "dynamics": "--dynamics",
    "credit": "--credits",
    "update": "--updates",
    "plasticity": "--plasticities",
}

_ABORT = [False]

# Prior knowledge: configurations already confirmed at high fidelity (TODO61
# maturation). Seeding the state with these means the exploit ladder starts in
# a productive region instead of narrowing onto L0 noise.
KNOWN_GOOD: list[dict] = [
    {
        "substrate": "memristive", "geometry": "tile_mesh",
        "dynamics": "instantaneous", "credit": "target_inversion",
        "update": "ortho_adam", "plasticity": "conflict_adaptive", "acc": 0.958,
    },
    {
        "substrate": "optical", "geometry": "tile_mesh",
        "dynamics": "instantaneous", "credit": "target_inversion",
        "update": "ortho_adam", "plasticity": "conflict_adaptive", "acc": 0.953,
    },
    {
        "substrate": "memristive", "geometry": "tile_mesh",
        "dynamics": "energy_minimization", "credit": "target_inversion",
        "update": "ortho_adam", "plasticity": "routing", "acc": 0.953,
    },
]


def _handle_signal(signum, frame):
    _ABORT[0] = True


def available_primitives() -> dict[str, list[str]]:
    """Every available primitive per structural axis, from the one registry."""
    from computronium.experiment.schema.axis import AXES_REGISTRIES, StructuralAxis

    return {
        axis.value: sorted(
            name for name, spec in AXES_REGISTRIES[axis].items() if spec.available
        )
        for axis in StructuralAxis
    }


def load_state() -> dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {
        "cycle": 0,
        "best_acc": max((c["acc"] for c in KNOWN_GOOD), default=0.0),
        "top": list(KNOWN_GOOD),
        "history": [],
    }


def _cell_key(cell: dict) -> tuple:
    return (
        cell.get("substrate"), cell.get("geometry"), cell.get("dynamics"),
        cell.get("credit"), cell.get("update"), cell.get("plasticity"),
    )


def merge_top(state: dict, measured: list[dict], k: int = 10) -> list[dict]:
    """Merge prior knowledge with measured cells, best accuracy per cell."""
    merged: dict[tuple, dict] = {}
    for cell in list(state.get("top", [])) + measured:
        key = _cell_key(cell)
        if key not in merged or cell["acc"] > merged[key]["acc"]:
            merged[key] = cell
    return sorted(merged.values(), key=lambda c: c["acc"], reverse=True)[:k]


def save_state(state: dict) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2))


def append_ledger(row: dict) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    with LEDGER_FILE.open("a") as f:
        f.write(json.dumps(row) + "\n")


def query_best(k: int = 10) -> tuple[float, list[dict]]:
    """Cumulative top-K cells by validation accuracy, plus the best accuracy."""
    import duckdb

    if not STORE_FILE.exists():
        return 0.0, []
    conn = duckdb.connect(str(STORE_FILE), read_only=True)
    try:
        rows = conn.execute(
            """
            SELECT substrate, geometry, dynamics, credit, update, plasticity,
                   MAX(CAST(json_extract(payload, '$.val_acc') AS REAL)) AS acc
            FROM records
            WHERE CAST(json_extract(payload, '$.val_acc') AS REAL) IS NOT NULL
            GROUP BY 1, 2, 3, 4, 5, 6
            ORDER BY acc DESC
            LIMIT ?
            """,
            [k],
        ).fetchall()
    finally:
        conn.close()
    top = [
        {
            "substrate": r[0],
            "geometry": r[1],
            "dynamics": r[2],
            "credit": r[3],
            "update": r[4],
            "plasticity": r[5],
            "acc": float(r[6]),
        }
        for r in rows
    ]
    best = max((c["acc"] for c in top), default=0.0)
    return best, top


def propose(state: dict, kind: str) -> tuple[list[str], dict]:
    """Axis flags and run knobs for the next cycle."""
    if kind == "explore":
        prims = available_primitives()
        flags: list[str] = []
        for axis, flag in AXIS_FLAGS.items():
            flags += [flag, ",".join(prims[axis])]
        return flags, {
            "fidelity": "L0",
            "epochs": 1,
            "n_seeds": 1,
            "batch_limit": 2000,
            "hours": 0.03,
            "sweep_steps": 5,
        }

    top = state.get("top", [])
    if not top:
        return propose(state, "explore")
    union: dict[str, set[str]] = {axis: set() for axis in AXIS_FLAGS}
    for cell in top:
        for axis in AXIS_FLAGS:
            if cell.get(axis):
                union[axis].add(cell[axis])
    flags = []
    for axis, flag in AXIS_FLAGS.items():
        values = sorted(union[axis])
        if values:
            flags += [flag, ",".join(values)]
    return flags, {
        "fidelity": "L1",
        "epochs": 3,
        "n_seeds": 1,
        "batch_limit": 0,
        "hours": 0.05,
        "sweep_steps": 10,
    }


def run_cycle(flags: list[str], knobs: dict, cycle: int, device: str) -> int:
    """Run one bounded experiment cycle via run_experiment.py. Returns exit code."""
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_path = LOG_DIR / f"continuous_cycle_{cycle:03d}.log"
    cmd = [
        "uv", "run", "python", "scripts/run_experiment.py",
        "--hours", str(knobs["hours"]),
        "--profile", "production-map",
        "--device", device,
        "--fidelity", knobs["fidelity"],
        "--epochs", str(knobs["epochs"]),
        "--n-seeds", str(knobs["n_seeds"]),
        "--batch-limit", str(knobs["batch_limit"]),
        "--sweep-steps", str(knobs["sweep_steps"]),
        "--store", str(STORE_FILE),
        *flags,
    ]
    timeout = knobs["hours"] * 3600 + 120
    print(f"  $ {' '.join(cmd)}", flush=True)
    with log_path.open("w") as log:
        try:
            result = subprocess.run(
                cmd, stdout=log, stderr=subprocess.STDOUT, timeout=timeout
            )
            return result.returncode
        except subprocess.TimeoutExpired:
            print(f"  cycle {cycle} timed out after {timeout:.0f}s", flush=True)
            return 124


def main() -> int:
    parser = argparse.ArgumentParser(description="Continuous experiment controller")
    parser.add_argument("--hours", type=float, default=4.0, help="Total budget (hours)")
    parser.add_argument("--cycles", type=int, default=0, help="Stop after N cycles (0=budget)")
    parser.add_argument("--device", choices=["auto", "cpu", "cuda"], default="cuda")
    args = parser.parse_args()

    signal.signal(signal.SIGINT, _handle_signal)
    signal.signal(signal.SIGTERM, _handle_signal)

    STATE_DIR.mkdir(parents=True, exist_ok=True)
    state = load_state()
    deadline = time.time() + args.hours * 3600
    cycle = state.get("cycle", 0)
    start_cycle = cycle

    print("=" * 70, flush=True)
    print("CONTINUOUS EXPERIMENT CONTROLLER", flush=True)
    print(f"  store:   {STORE_FILE}", flush=True)
    print(f"  ledger:  {LEDGER_FILE}", flush=True)
    print(f"  resume:  cycle {cycle}, best_acc {state.get('best_acc', 0.0):.3f}", flush=True)
    print(f"  budget:  {args.hours}h", flush=True)
    print("=" * 70, flush=True)

    while not _ABORT[0]:
        if args.cycles and (cycle - start_cycle) >= args.cycles:
            print("Cycle limit reached.", flush=True)
            break
        if time.time() >= deadline:
            print("Budget exhausted.", flush=True)
            break

        kind = "explore" if cycle % 2 == 0 else "exploit"
        flags, knobs = propose(state, kind)
        print(f"\n[cycle {cycle}] {kind} ({knobs['fidelity']}, {knobs['hours']*60:.1f} min)", flush=True)
        rc = run_cycle(flags, knobs, cycle, args.device)

        _, measured = query_best()
        top = merge_top(state, measured)
        best = max((c["acc"] for c in top), default=0.0)
        improvement = best - state.get("best_acc", 0.0)
        state["best_acc"] = max(best, state.get("best_acc", 0.0))
        state["top"] = top
        state["cycle"] = cycle + 1
        state["history"].append(
            {"cycle": cycle, "kind": kind, "best": best, "rc": rc}
        )
        save_state(state)
        append_ledger(
            {
                "cycle": cycle,
                "kind": kind,
                "fidelity": knobs["fidelity"],
                "rc": rc,
                "best_acc": best,
                "improvement": improvement,
                "top": top[:3],
                "ts": time.time(),
            }
        )
        top_str = ", ".join(f"{c['acc']:.3f}" for c in top[:3]) or "none"
        print(
            f"  → best={best:.4f} (Δ{improvement:+.4f})  top3=[{top_str}]  rc={rc}",
            flush=True,
        )
        cycle += 1

    print("\n" + "=" * 70, flush=True)
    print(f"CONTROLLER STOPPED at cycle {cycle}  best_acc={state['best_acc']:.4f}", flush=True)
    if state.get("top"):
        print("Top cells:", flush=True)
        for c in state["top"][:5]:
            print(
                f"  {c['acc']:.4f}  {c['substrate']}/{c['geometry']}/{c['dynamics']}"
                f"/{c['credit']}/{c['update']}/{c['plasticity']}",
                flush=True,
            )
    print("=" * 70, flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
