#!/usr/bin/env python3
"""Campaign Analysis — Automated KB inspection for continuous discovery loop.

Usage:
    uv run python scripts/campaign_analyze.py --root artifacts/broad_map/mnist
    uv run python scripts/campaign_analyze.py --root artifacts/broad_map/mnist --json
"""

from __future__ import annotations

import argparse
import json
import sqlite3
from collections import Counter, defaultdict
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any


@dataclass
class ClampStats:
    dynamics: str
    credit: str
    update: str
    total_cells: int
    clamp_count: int
    clamp_rate: float


@dataclass
class SpectralStats:
    dynamics: str
    max_sr: float
    avg_sr: float
    count: int
    over_1: int
    over_05: int


@dataclass
class ParamStats:
    topology: str
    max_params: int
    avg_params: int
    over_budget: int
    budget: int


@dataclass
class ParetoStats:
    front_size: int
    accuracy_range: tuple[float, float]
    walltime_range: tuple[float, float]
    spread_pct: float


@dataclass
class VoidStats:
    category: str
    count: int
    examples: list[str]


@dataclass
class DefectStats:
    combo: str
    dynamics: str
    credit: str
    update: str
    topology: str
    defect_type: str  # "nan_loss", "exploding_loss", "very_low_acc"
    value: float
    count: int


def load_experiments(kb_path: Path, task: str) -> list[dict]:
    """Load all experiment entries from KB."""
    conn = sqlite3.connect(kb_path)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT id, metrics, hyperparameters FROM knowledge WHERE topic LIKE ? AND source = 'experiment'",
        (f"experiment:{task}",),
    ).fetchall()
    conn.close()

    exps = []
    for row in rows:
        metrics = json.loads(row["metrics"]) if row["metrics"] else {}
        hp = json.loads(row["hyperparameters"]) if row["hyperparameters"] else {}
        geometry = (
            hp.get("geometry", {}) if isinstance(hp.get("geometry"), dict) else {}
        )
        exps.append({
            "id": row["id"],
            "metrics": metrics,
            "hp": hp,
            "geometry": geometry,
            "dynamics": hp.get("dynamics", "unknown"),
            "credit": hp.get("credit", "unknown"),
            "update": hp.get("update", "unknown"),
            "topology": geometry.get("topology_type", "unknown"),
        })
    return exps


def load_voids(kb_path: Path, task: str) -> list[dict]:
    """Load structural voids from KB."""
    conn = sqlite3.connect(kb_path)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        'SELECT dynamics, credit, "update", topology, category, error FROM structural_voids WHERE task = ?',
        (task,),
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def analyze_clamps(exps: list[dict]) -> list[ClampStats]:
    """Analyze energy clamp frequency by (dynamics, credit, update)."""
    groups: dict[tuple[str, str, str], dict[str, int]] = defaultdict(
        lambda: {"total": 0, "clamps": 0}
    )

    for exp in exps:
        key = (exp["dynamics"], exp["credit"], exp["update"])
        groups[key]["total"] += 1
        clamp_count = exp["metrics"].get("energy_clamp_count", 0)
        if clamp_count > 0:
            groups[key]["clamps"] += 1

    stats = []
    for (dyn, cred, upd), counts in sorted(
        groups.items(), key=lambda x: -x[1]["clamps"] / max(x[1]["total"], 1)
    ):
        rate = counts["clamps"] / max(counts["total"], 1)
        if counts["total"] >= 1:  # Only report if we have data
            stats.append(
                ClampStats(dyn, cred, upd, counts["total"], counts["clamps"], rate)
            )
    return stats


def analyze_spectral(exps: list[dict]) -> list[SpectralStats]:
    """Analyze spectral radius by dynamics."""
    groups: dict[str, list[float]] = defaultdict(list)

    for exp in exps:
        sr = exp["metrics"].get("spectral_radius", 0)
        if sr > 0:
            groups[exp["dynamics"]].append(sr)

    stats = []
    for dyn, srs in sorted(groups.items(), key=lambda x: -max(x[1])):
        stats.append(
            SpectralStats(
                dynamics=dyn,
                max_sr=max(srs),
                avg_sr=sum(srs) / len(srs),
                count=len(srs),
                over_1=sum(1 for s in srs if s > 1.0),
                over_05=sum(1 for s in srs if s > 0.5),
            )
        )
    return stats


def analyze_params(exps: list[dict], budget: int) -> list[ParamStats]:
    """Analyze param count by topology."""
    groups: dict[str, list[int]] = defaultdict(list)

    for exp in exps:
        pc = exp["metrics"].get("param_count", 0)
        if pc > 0:
            groups[exp["topology"]].append(int(pc))

    stats = []
    for topo, pcs in sorted(groups.items(), key=lambda x: -max(x[1])):
        stats.append(
            ParamStats(
                topology=topo,
                max_params=max(pcs),
                avg_params=sum(pcs) // len(pcs),
                over_budget=sum(1 for p in pcs if p > budget * 1.5),
                budget=budget,
            )
        )
    return stats


def analyze_pareto(exps: list[dict]) -> ParetoStats:
    """Compute Pareto front spread."""
    if not exps:
        return ParetoStats(0, (0, 0), (0, 0), 0.0)

    # Extract objectives (accuracy, walltime)
    points = []
    for exp in exps:
        acc = exp["metrics"].get("final_accuracy", 0)
        wt = exp["metrics"].get("walltime_s", 0)
        if acc > 0 and wt > 0:
            points.append((acc, wt))

    if len(points) < 2:
        return ParetoStats(len(points), (0, 0), (0, 0), 0.0)

    # Simple Pareto: non-dominated on (accuracy ↑, walltime ↓)
    pareto = []
    for i, (acc_i, wt_i) in enumerate(points):
        dominated = False
        for j, (acc_j, wt_j) in enumerate(points):
            if (
                i != j
                and acc_j >= acc_i
                and wt_j <= wt_i
                and (acc_j > acc_i or wt_j < wt_i)
            ):
                dominated = True
                break
        if not dominated:
            pareto.append((acc_i, wt_i))

    accs = [p[0] for p in pareto]
    wts = [p[1] for p in pareto]
    acc_range = (min(accs), max(accs))
    wt_range = (min(wts), max(wts))
    spread = (acc_range[1] - acc_range[0]) * 100  # percentage points

    return ParetoStats(len(pareto), acc_range, wt_range, spread)


def analyze_numerical_defects(exps: list[dict]) -> list[DefectStats]:
    """Detect numerical defects: NaN loss, exploding loss, very low accuracy."""
    groups: dict[tuple[str, str, str, str], list[dict]] = defaultdict(list)
    
    for exp in exps:
        key = (exp["dynamics"], exp["credit"], exp["update"], exp["topology"])
        groups[key].append(exp)
    
    defects = []
    for (dyn, cred, upd, topo), exps_list in groups.items():
        if len(exps_list) < 1:
            continue
        
        nan_count = 0
        exploding_count = 0
        very_low_acc_count = 0
        
        for exp in exps_list:
            metrics = exp["metrics"]
            loss = metrics.get("final_loss", 0)
            acc = metrics.get("final_accuracy", 0)
            
            if isinstance(loss, float) and loss != loss:  # NaN
                nan_count += 1
            elif isinstance(loss, float) and loss > 100:
                exploding_count += 1
            elif acc < 0.05:
                very_low_acc_count += 1
        
        if nan_count > 0:
            defects.append(DefectStats(
                combo=f"{dyn}|{cred}|{upd}|{topo}",
                dynamics=dyn, credit=cred, update=upd, topology=topo,
                defect_type="nan_loss", value=float(nan_count), count=nan_count
            ))
        if exploding_count > 0:
            # Get max exploding loss for this combo
            max_loss = max(
                exp["metrics"].get("final_loss", 0) 
                for exp in exps_list 
                if isinstance(exp["metrics"].get("final_loss", 0), float) and exp["metrics"].get("final_loss", 0) > 100
            )
            defects.append(DefectStats(
                combo=f"{dyn}|{cred}|{upd}|{topo}",
                dynamics=dyn, credit=cred, update=upd, topology=topo,
                defect_type="exploding_loss", value=max_loss, count=exploding_count
            ))
        if very_low_acc_count > 0 and len(exps_list) == very_low_acc_count:
            # All runs for this combo have very low accuracy
            defects.append(DefectStats(
                combo=f"{dyn}|{cred}|{upd}|{topo}",
                dynamics=dyn, credit=cred, update=upd, topology=topo,
                defect_type="very_low_acc", value=0.0, count=very_low_acc_count
            ))
    
    return defects


def analyze_voids(voids: list[dict]) -> list[VoidStats]:
    """Summarize voids by category."""
    groups: dict[str, list[dict]] = defaultdict(list)
    for v in voids:
        groups[v["category"]].append(v)

    stats = []
    for cat, items in sorted(groups.items(), key=lambda x: -len(x[1])):
        examples = [
            f"{v['dynamics']}|{v['credit']}|{v['update']}|{v['topology']}"
            for v in items[:3]
        ]
        stats.append(VoidStats(cat, len(items), examples))
    return stats


def find_worst_combos(exps: list[dict], top_n: int = 3) -> list[dict]:
    """Find worst-performing (dynamics, credit, update) combos by median accuracy."""
    groups: dict[tuple[str, str, str], list[float]] = defaultdict(list)

    for exp in exps:
        acc = exp["metrics"].get("final_accuracy", 0)
        if acc > 0:
            groups[(exp["dynamics"], exp["credit"], exp["update"])].append(acc)

    results = []
    for combo, accs in groups.items():
        if len(accs) >= 1:
            import statistics

            results.append({
                "dynamics": combo[0],
                "credit": combo[1],
                "update": combo[2],
                "median_accuracy": statistics.median(accs),
                "count": len(accs),
            })

    return sorted(results, key=lambda x: x["median_accuracy"])[:top_n]


def main():
    parser = argparse.ArgumentParser(
        description="Analyze campaign KB for continuous discovery loop"
    )
    parser.add_argument(
        "--root", type=Path, required=True, help="Campaign root (contains kb.sqlite)"
    )
    parser.add_argument("--task", default="mnist", help="Task name")
    parser.add_argument(
        "--budget",
        type=int,
        default=25000,
        help="Parameter budget for blowup detection",
    )
    parser.add_argument(
        "--json", action="store_true", help="Output JSON instead of human-readable"
    )
    args = parser.parse_args()

    kb_path = args.root / "kb.sqlite"
    if not kb_path.exists():
        print(f"ERROR: KB not found at {kb_path}")
        return 1

    exps = load_experiments(kb_path, args.task)
    voids = load_voids(kb_path, args.task)

    if not exps:
        print("No experiments found in KB")
        return 0

    # Run analyses
    clamp_stats = analyze_clamps(exps)
    spectral_stats = analyze_spectral(exps)
    param_stats = analyze_params(exps, args.budget)
    pareto_stats = analyze_pareto(exps)
    void_stats = analyze_voids(voids)
    worst_combos = find_worst_combos(exps)
    defect_stats = analyze_numerical_defects(exps)

    if args.json:
        output = {
            "clamps": [asdict(s) for s in clamp_stats],
            "spectral": [asdict(s) for s in spectral_stats],
            "params": [asdict(s) for s in param_stats],
            "pareto": asdict(pareto_stats),
            "voids": [asdict(s) for s in void_stats],
            "worst_combos": worst_combos,
            "defects": [asdict(s) for s in defect_stats],
        }
        print(json.dumps(output, indent=2))
        return 0

    # Human-readable output
    print(f"\n{'=' * 60}")
    print(f"CAMPAIGN ANALYSIS: {args.root} (task={args.task})")
    print(f"{'=' * 60}")
    print(f"Total experiments: {len(exps)}")
    print(f"Total voids: {len(voids)}")
    print(f"Parameter budget: {args.budget}")

    # Clamps
    print(f"\n--- ENERGY CLAMPS ---")
    clamp_warnings = [s for s in clamp_stats if s.clamp_rate > 0.2]
    if clamp_warnings:
        print(f"⚠️  {len(clamp_warnings)} combos exceed 20% clamp rate:")
        for s in clamp_warnings:
            print(
                f"   {s.dynamics} × {s.credit} × {s.update}: {s.clamp_rate:.1%} ({s.clamp_count}/{s.total_cells})"
            )
    else:
        print("✅ All clamp rates < 20%")

    # Spectral
    print(f"\n--- SPECTRAL RADIUS ---")
    spectral_warnings = [s for s in spectral_stats if s.over_1 > 0]
    if spectral_warnings:
        print(f"⚠️  {len(spectral_warnings)} dynamics have spectral_radius > 1.0:")
        for s in spectral_warnings:
            print(
                f"   {s.dynamics}: max={s.max_sr:.4f}, avg={s.avg_sr:.4f}, >1.0: {s.over_1}/{s.count}"
            )
    else:
        print("✅ All spectral radii < 1.0")

    # Params
    print(f"\n--- PARAM COUNT ---")
    param_warnings = [s for s in param_stats if s.over_budget > 0]
    if param_warnings:
        print(f"⚠️  {len(param_warnings)} topologies exceed 1.5x budget:")
        for s in param_warnings:
            print(
                f"   {s.topology}: max={s.max_params:,}, avg={s.avg_params:,}, >1.5x: {s.over_budget}"
            )
    else:
        print("✅ All param counts within 1.5x budget")

    # Pareto
    print(f"\n--- PARETO FRONT ---")
    print(f"   Front size: {pareto_stats.front_size}")
    print(
        f"   Accuracy range: {pareto_stats.accuracy_range[0]:.4f} – {pareto_stats.accuracy_range[1]:.4f}"
    )
    print(
        f"   Walltime range: {pareto_stats.walltime_range[0]:.1f}s – {pareto_stats.walltime_range[1]:.1f}s"
    )
    print(f"   Spread: {pareto_stats.spread_pct:.1f} percentage points")
    if pareto_stats.spread_pct < 20:
        print("   ⚠️  Low spread — consider objective-space bias in driver")

    # Voids
    print(f"\n--- VOIDS ({len(voids)} total) ---")
    for s in void_stats:
        print(f"   {s.category}: {s.count}")
        for ex in s.examples:
            print(f"      e.g., {ex}")

    # Worst combos
    print(f"\n--- TOP {len(worst_combos)} WORST COMBOS (by median accuracy) ---")
    for i, w in enumerate(worst_combos, 1):
        print(
            f"   {i}. {w['dynamics']} × {w['credit']} × {w['update']}: median_acc={w['median_accuracy']:.4f} (n={w['count']})"
        )

    # Numerical defects
    print(f"\n--- NUMERICAL DEFECTS ---")
    if defect_stats:
        print(f"⚠️  {len(defect_stats)} combos have numerical defects:")
        for s in defect_stats:
            print(f"   {s.defect_type}: {s.combo} (count={s.count}, value={s.value})")
    else:
        print("✅ No numerical defects detected")

    print(f"\n{'=' * 60}")
    print("NEXT: Apply fixes for ⚠️ items, then re-run burst")
    print(f"{'=' * 60}\n")

    return 0


if __name__ == "__main__":
    exit(main())
