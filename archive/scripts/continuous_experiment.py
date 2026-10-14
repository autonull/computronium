#!/usr/bin/env python3
"""Continuous experiment controller — fully automatic propose→run→analyze→repeat.

One script. It runs bounded experiment cycles back to back, classifies each,
narrows away from defects, and rewrites a live report every cycle. Resumable:
re-running continues from ``state.json``. No human input between cycles.

Outputs (all under ``experiments/continuous/``):
  ``ledger.jsonl``      per-cycle structured record (the fix-data)
  ``defects.jsonl``     defect signatures + suggested fixes
  ``report.md``         human-readable live summary
  ``state.json``        resumable state (cycle, best, top-K, force_explore)
  ``continuous.duckdb`` cumulative evidence store
  ``logs/continuous_cycle_NNN.log``  per-cycle raw output

Usage:
    uv run python scripts/continuous_experiment.py --hours 8 --device cuda
    uv run python scripts/continuous_experiment.py --cycles 3 --device cuda
"""

from __future__ import annotations

import argparse
import json
import re
import signal
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATE_DIR = ROOT / "experiments" / "continuous"
STATE_FILE = STATE_DIR / "state.json"
LEDGER_FILE = STATE_DIR / "ledger.jsonl"
DEFECTS_FILE = STATE_DIR / "defects.jsonl"
REPORT_FILE = STATE_DIR / "report.md"
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

# Prior knowledge: configurations already confirmed at high fidelity (TODO61).
# Seeding the state with these means the exploit ladder starts productive.
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

# Defect signature → suggested fix (for the process-improvement half of the loop).
FIX_HINTS = {
    "shapes cannot be multiplied": (
        "D1: geometry×credit shape mismatch — fix the tile_mesh forward for "
        "gradient credit, or reject the combo in SystemConfig.validate (D4)."
    ),
    "yielded nothing": (
        "D2/D4: search space empty for this axis config — widen axes, or the "
        "combo is silently filtered by the dry-run gate (validation gap)."
    ),
    "no cells measured": (
        "D2/D4: a whole cycle produced no cells — axis config too narrow or "
        "fully broken. Widened to explore."
    ),
}


def _handle_signal(signum, frame):
    _ABORT[0] = True


# ── state ────────────────────────────────────────────────────────────────────

def load_state() -> dict:
    if STATE_FILE.exists():
        state = json.loads(STATE_FILE.read_text())
        state.setdefault("force_explore", False)
        state.setdefault("history", [])
        return state
    return {
        "cycle": 0,
        "best_acc": max((c["acc"] for c in KNOWN_GOOD), default=0.0),
        "top": list(KNOWN_GOOD),
        "history": [],
        "force_explore": False,
    }


def save_state(state: dict) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2))


def append_jsonl(path: Path, row: dict) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    with path.open("a") as f:
        f.write(json.dumps(row) + "\n")


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


# ── registry / evidence ──────────────────────────────────────────────────────

def available_primitives() -> dict[str, list[str]]:
    from computronium.experiment.schema.axis import AXES_REGISTRIES, StructuralAxis

    return {
        axis.value: sorted(
            name for name, spec in AXES_REGISTRIES[axis].items() if spec.available
        )
        for axis in StructuralAxis
    }


def query_best(k: int = 10) -> list[dict]:
    """Cumulative top-K cells by validation accuracy from the store (with retry)."""
    import duckdb
    import time

    if not STORE_FILE.exists():
        return []
    for attempt in range(10):
        try:
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
            return [
                {
                    "substrate": r[0], "geometry": r[1], "dynamics": r[2],
                    "credit": r[3], "update": r[4], "plasticity": r[5], "acc": float(r[6]),
                }
                for r in rows
            ]
        except duckdb.IOException as e:
            if "Could not set lock" in str(e) and attempt < 9:
                time.sleep(0.2 * (attempt + 1))
                continue
            raise
    return []


# ── cycle classification ─────────────────────────────────────────────────────

def classify_cycle(log_path: Path) -> dict:
    """Parse a cycle's raw log into a structured result."""
    text = log_path.read_text() if log_path.exists() else ""
    m = re.search(r"Cells measured:\s*(\d+)", text)
    n_cells = int(m.group(1)) if m else 0
    failures = re.findall(r"Cell \d+ FAILED: (.+)", text)
    signatures = sorted({
        sig for sig in FIX_HINTS if sig in text
    } | {
        f.splitlines()[0][:120] for f in failures
    })
    empty = ("yielded nothing" in text) or ("no cells measured" in text)
    return {
        "n_cells": n_cells,
        "n_failures": len(failures),
        "failures": failures[:5],
        "signatures": signatures,
        "empty": empty,
    }


def record_defects(cycle: int, flags: list[str], cls: dict) -> None:
    for sig in cls["signatures"]:
        append_jsonl(DEFECTS_FILE, {
            "cycle": cycle,
            "signature": sig,
            "axis_config": " ".join(flags),
            "hint": FIX_HINTS.get(sig, ""),
            "ts": time.time(),
        })


# ── proposal ─────────────────────────────────────────────────────────────────

def propose(state: dict, kind: str) -> tuple[list[str], dict]:
    """Axis flags and run knobs for the next cycle."""
    if kind == "explore" or state.get("force_explore"):
        state["force_explore"] = False
        prims = available_primitives()
        flags: list[str] = []
        for axis, flag in AXIS_FLAGS.items():
            flags += [flag, ",".join(prims[axis])]
        return flags, {
            "fidelity": "L0", "epochs": 1, "n_seeds": 1,
            "batch_limit": 2000, "hours": 0.03, "sweep_steps": 5,
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
        "fidelity": "L1", "epochs": 3, "n_seeds": 1,
        "batch_limit": 0, "hours": 0.05, "sweep_steps": 10,
    }


# ── execution ────────────────────────────────────────────────────────────────

def run_cycle(flags: list[str], knobs: dict, cycle: int, device: str) -> tuple[int, Path]:
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
    timeout = knobs["hours"] * 3600 + 180
    print(f"  $ {' '.join(cmd)}", flush=True)
    with log_path.open("w") as log:
        try:
            result = subprocess.run(cmd, stdout=log, stderr=subprocess.STDOUT, timeout=timeout)
            return result.returncode, log_path
        except subprocess.TimeoutExpired:
            return 124, log_path


# ── report ───────────────────────────────────────────────────────────────────

def write_report(state: dict, last: dict | None) -> None:
    lines = [
        "# Continuous Experiment Report",
        "",
        f"- **cycle**: {state['cycle']}",
        f"- **best accuracy**: {state['best_acc']:.4f}",
        f"- **store**: `{STORE_FILE.relative_to(ROOT)}`",
        "",
    ]
    if last:
        lines += [
            "## Last cycle",
            f"- kind: {last['kind']}  fidelity: {last['fidelity']}",
            f"- cells measured: {last['n_cells']}  failures: {last['n_failures']}",
            f"- empty space: {last['empty']}",
            "",
        ]
    lines += ["## Top cells", "", "| acc | substrate | geometry | dynamics | credit | update | plasticity |",
              "|----:|---|---|---|---|---|---|"]
    for c in state.get("top", [])[:10]:
        lines.append(
            f"| {c['acc']:.4f} | {c['substrate']} | {c['geometry']} | {c['dynamics']} "
            f"| {c['credit']} | {c['update']} | {c['plasticity']} |"
        )
    lines += ["", "## Cycle history", "", "| cycle | kind | best | Δ | cells | empty |",
              "|------:|------|-----:|--:|------:|-------|"]
    prev = 0.0
    for h in state.get("history", []):
        delta = h["best"] - prev
        prev = h["best"]
        lines.append(
            f"| {h['cycle']} | {h['kind']} | {h['best']:.4f} | {delta:+.4f} "
            f"| {h.get('n_cells', '?')} | {h.get('empty', '?')} |"
        )
    if DEFECTS_FILE.exists():
        defects = [json.loads(l) for l in DEFECTS_FILE.read_text().splitlines() if l.strip()]
        lines += ["", "## Defects (fix-data)", ""]
        seen: set[str] = set()
        for d in defects:
            sig = d["signature"]
            if sig in seen:
                continue
            seen.add(sig)
            lines.append(f"- `{sig}`")
            if d.get("hint"):
                lines.append(f"  - {d['hint']}")
    REPORT_FILE.write_text("\n".join(lines) + "\n")


# ── main ─────────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(description="Continuous experiment controller")
    parser.add_argument("--hours", type=float, default=8.0, help="Total budget (hours)")
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
    print(f"  report:  {REPORT_FILE}", flush=True)
    print(f"  resume:  cycle {cycle}, best_acc {state.get('best_acc', 0.0):.4f}", flush=True)
    print(f"  budget:  {args.hours}h", flush=True)
    print("=" * 70, flush=True)

    last = None
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
        rc, log_path = run_cycle(flags, knobs, cycle, args.device)
        cls = classify_cycle(log_path)

        if cls["empty"]:
            state["force_explore"] = True
        record_defects(cycle, flags, cls)

        measured = query_best()
        top = merge_top(state, measured)
        best = max((c["acc"] for c in top), default=0.0)
        improvement = best - state.get("best_acc", 0.0)
        state["best_acc"] = max(best, state.get("best_acc", 0.0))
        state["top"] = top
        state["cycle"] = cycle + 1
        state["history"].append({
            "cycle": cycle, "kind": kind, "best": best, "rc": rc,
            "n_cells": cls["n_cells"], "empty": cls["empty"],
        })
        save_state(state)

        last = {
            "cycle": cycle, "kind": kind, "fidelity": knobs["fidelity"],
            "rc": rc, "best": best, "n_cells": cls["n_cells"],
            "n_failures": cls["n_failures"], "empty": cls["empty"],
            "signatures": cls["signatures"],
        }
        append_jsonl(LEDGER_FILE, {**last, "top": top[:3], "ts": time.time()})
        write_report(state, last)

        print(
            f"  → best={best:.4f} (Δ{improvement:+.4f})  cells={cls['n_cells']} "
            f"failures={cls['n_failures']}  empty={cls['empty']}  rc={rc}",
            flush=True,
        )
        cycle += 1

    write_report(state, last)
    print("\n" + "=" * 70, flush=True)
    print(f"CONTROLLER STOPPED at cycle {cycle}  best_acc={state['best_acc']:.4f}", flush=True)
    print(f"report: {REPORT_FILE}", flush=True)
    print("=" * 70, flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
