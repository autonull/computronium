"""Learn void rules from cells.jsonl refusals.

Analyzes refusal patterns in experimental data to auto-generate void rules
that replace hand-coded ones in legality/void_rules.py.

Rule: For each (geometry, credit, dynamics) tuple:
- If refused_rate > 0.8 and measured_count > 5 → add void rule
- If measured_count > 10 and all viable → remove void rule
"""

from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

__all__ = [
    "VoidRuleCandidate",
    "generate_void_rules_file",
    "learn_void_rules",
]


@dataclass(frozen=True, slots=True)
class VoidRuleCandidate:
    """A candidate void rule learned from data."""

    axis_a: str
    value_a: str
    axis_b: str
    value_b: str
    refused_count: int
    measured_count: int
    refused_rate: float
    action: str  # "add" or "remove"


def _extract_axes(screen: dict[str, Any]) -> dict[str, str]:
    """Extract axis values from a screen box."""
    box = screen.get("box", {})
    axes = {}
    for key in ("substrate", "geometry", "dynamics", "plasticity", "credit", "update"):
        if key in box:
            axes[key] = box[key]
    return axes


def _count_pair_stats(
    cells_path: Path,
) -> dict[tuple[str, str, str, str], dict[str, int]]:
    """Count refusals and measurements per axis pair from cells.jsonl."""
    pair_stats: dict[tuple[str, str, str, str], dict[str, int]] = defaultdict(
        lambda: {"refused": 0, "measured": 0, "total": 0}
    )

    with cells_path.open(encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            c = json.loads(line)
            screen = c.get("screen", {})
            status = screen.get("status", "")
            axes = _extract_axes(screen)

            # Consider all pairs of axes
            axis_names = list(axes.keys())
            for i, a1 in enumerate(axis_names):
                for a2 in axis_names[i + 1 :]:
                    v1, v2 = axes[a1], axes[a2]
                    # Order consistently
                    key = (a2, v2, a1, v1) if (a1, v1) > (a2, v2) else (a1, v1, a2, v2)

                    stats = pair_stats[key]
                    stats["total"] += 1
                    if status in {"REFUSED", "UNAVAILABLE"}:
                        stats["refused"] += 1
                    elif status == "MEASURED":
                        stats["measured"] += 1

    return pair_stats


def _generate_candidates(
    pair_stats: dict[tuple[str, str, str, str], dict[str, int]],
    refused_threshold: float,
    min_measured_for_add: int,
    min_measured_for_remove: int,
) -> list[VoidRuleCandidate]:
    """Generate void rule candidates from pair statistics."""
    candidates = []
    for (a1, v1, a2, v2), stats in pair_stats.items():
        refused = stats["refused"]
        measured = stats["measured"]
        total = stats["total"]

        if total == 0:
            continue

        refused_rate = refused / total if total > 0 else 0.0

        # Rule to ADD void rule: high refusal rate, enough measured samples
        if refused_rate > refused_threshold and measured >= min_measured_for_add:
            candidates.append(
                VoidRuleCandidate(
                    axis_a=a1,
                    value_a=v1,
                    axis_b=a2,
                    value_b=v2,
                    refused_count=refused,
                    measured_count=measured,
                    refused_rate=refused_rate,
                    action="add",
                )
            )

        # Rule to REMOVE void rule: many measured, all viable (no refusals)
        if measured >= min_measured_for_remove and refused == 0:
            candidates.append(
                VoidRuleCandidate(
                    axis_a=a1,
                    value_a=v1,
                    axis_b=a2,
                    value_b=v2,
                    refused_count=refused,
                    measured_count=measured,
                    refused_rate=0.0,
                    action="remove",
                )
            )

    return candidates


def learn_void_rules(
    cells_path: Path,
    refused_threshold: float = 0.8,
    min_measured_for_add: int = 5,
    min_measured_for_remove: int = 10,
) -> list[VoidRuleCandidate]:
    """Learn void rules from cells.jsonl.

    Args:
        cells_path: Path to cells.jsonl
        refused_threshold: Refusal rate above which to add void rule
        min_measured_for_add: Minimum measured count to consider adding void rule
        min_measured_for_remove: Minimum measured count to consider removing void rule

    Returns:
        List of VoidRuleCandidate with action "add" or "remove"
    """
    if not cells_path.exists():
        raise FileNotFoundError(f"File not found: {cells_path}")

    pair_stats = _count_pair_stats(cells_path)
    return _generate_candidates(
        pair_stats,
        refused_threshold,
        min_measured_for_add,
        min_measured_for_remove,
    )


def generate_void_rules_file(
    candidates: list[VoidRuleCandidate],
    output_path: Path,
    existing_void_rules: dict[tuple[str, str, str, str], str] | None = None,
) -> None:
    """Generate a Python file with learned void rules.

    Args:
        candidates: List of VoidRuleCandidate from learn_void_rules
        output_path: Path to write the generated file
        existing_void_rules: Optional dict of existing rules to preserve
    """
    existing_void_rules = existing_void_rules or {}

    lines = [
        '"""Learned void rules from cells.jsonl analysis."""',
        "",
        "# AUTO-GENERATED by learn_void_rules.py",
        "# DO NOT EDIT MANUALLY - regenerate after new experimental data",
        "",
        "from computronium.experiment.legality.classify import (",
        "    DEFECT_REGISTRY,",
        "    DefectClass,",
        "    VoidReason,",
        ")",
        "",
        "",
        "# Rules to ADD (high refusal rate)",
        "ADD_RULES = [",
    ]

    for c in candidates:
        if c.action == "add":
            # Map to defect class and void reason
            defect_class, void_reason = _map_to_defect(c.axis_a, c.axis_b)
            lines.append(
                f'    ("{c.axis_a}", "{c.value_a}", "{c.axis_b}", "{c.value_b}", '
                f"DefectClass.{defect_class}, VoidReason.{void_reason}),  # "
                f"refused_rate={c.refused_rate:.2f}, measured={c.measured_count}"
            )

    lines.append("]")
    lines.append("")
    lines.append("# Rules to REMOVE (all viable, no refusals)")
    lines.append("REMOVE_RULES = [")
    for c in candidates:
        if c.action == "remove":
            lines.append(
                f'    ("{c.axis_a}", "{c.value_a}", "{c.axis_b}", "{c.value_b}"),  # '
                f"measured={c.measured_count}, all_viable"
            )

    lines.append("]")
    lines.append("")
    lines.append("")
    lines.append("def apply_learned_rules() -> None:")
    lines.append('    """Apply learned void rules to the defect registry."""')
    lines.append("    for rule in ADD_RULES:")
    lines.append("        a1, v1, a2, v2, defect_class, void_reason = rule")
    lines.append("        key = (a1, v1, a2, v2)")
    lines.append("        if key not in existing_void_rules:")
    lines.append("            DEFECT_REGISTRY.register_void_pattern(")
    lines.append("                a1, v1, a2, v2, defect_class, void_reason")
    lines.append("            )")
    lines.append(
        "    # Note: REMOVE_RULES requires registry modification not supported yet"
    )
    lines.append("    # Manual review needed for removal")

    output_path.write_text("\n".join(lines), encoding="utf-8")


def _map_to_defect(axis_a: str, axis_b: str) -> tuple[str, str]:
    """Map axis pair to defect class and void reason."""
    pair = tuple(sorted([axis_a, axis_b]))
    mapping = {
        ("credit", "dynamics"): (
            "VOID_DYNAMICS_CREDIT",
            "INCOMPATIBLE_DYNAMICS_CREDIT",
        ),
        ("credit", "geometry"): (
            "VOID_CREDIT_GEOMETRY",
            "INCOMPATIBLE_CREDIT_GEOMETRY",
        ),
        ("credit", "plasticity"): (
            "VOID_CREDIT_PLASTICITY",
            "INCOMPATIBLE_CREDIT_PLASTICITY",
        ),
        ("credit", "substrate"): (
            "VOID_CREDIT_SUBSTRATE",
            "INCOMPATIBLE_CREDIT_SUBSTRATE",
        ),
        ("dynamics", "geometry"): (
            "VOID_GEOMETRY_DYNAMICS",
            "INCOMPATIBLE_GEOMETRY_DYNAMICS",
        ),
        ("dynamics", "plasticity"): (
            "VOID_DYNAMICS_PLASTICITY",
            "INCOMPATIBLE_DYNAMICS_PLASTICITY",
        ),
        ("dynamics", "substrate"): (
            "VOID_SUBSTRATE_DYNAMICS",
            "INCOMPATIBLE_SUBSTRATE_DYNAMICS",
        ),
        ("geometry", "plasticity"): (
            "VOID_GEOMETRY_PLASTICITY",
            "INCOMPATIBLE_GEOMETRY_PLASTICITY",
        ),
        ("geometry", "substrate"): (
            "VOID_SUBSTRATE_GEOMETRY",
            "INCOMPATIBLE_SUBSTRATE_GEOMETRY",
        ),
        ("plasticity", "substrate"): (
            "VOID_SUBSTRATE_PLASTICITY",
            "INCOMPATIBLE_SUBSTRATE_PLASTICITY",
        ),
    }
    return mapping.get(pair, ("VOID_UNCLASSIFIED", "INCOMPATIBLE_UNCLASSIFIED"))


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Learn void rules from cells.jsonl")
    parser.add_argument("--cells", type=str, default="results/sec/cells.jsonl")
    parser.add_argument(
        "--output",
        type=str,
        default="computronium/experiment/legality/void_rules_learned.py",
    )
    parser.add_argument("--refused-threshold", type=float, default=0.8)
    parser.add_argument("--min-measured-add", type=int, default=5)
    parser.add_argument("--min-measured-remove", type=int, default=10)

    args = parser.parse_args()

    candidates = learn_void_rules(
        Path(args.cells),
        refused_threshold=args.refused_threshold,
        min_measured_for_add=args.min_measured_add,
        min_measured_for_remove=args.min_measured_remove,
    )

    print(f"Found {len(candidates)} candidate rules:")
    for c in candidates:
        print(
            f"  {c.action.upper()}: {c.axis_a}={c.value_a} x {c.axis_b}={c.value_b} "
            f"(refused={c.refused_count}, measured={c.measured_count}, rate={c.refused_rate:.2f})"
        )

    generate_void_rules_file(candidates, Path(args.output))
    print(f"\nGenerated: {args.output}")
