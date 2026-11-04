"""Single-source budget allocation constants for smart-survey profile.

Shared between:
- experiment_shallow.sh (preview display)
- _promotion.py (promotion logic)
- _budget.py (deadline/budget enforcement)
"""

from __future__ import annotations

# Budget allocation fractions for smart-survey (L0/L1/L2)
# L0: 40% screen, L1: 40% confirm, L2: 20% deepen
BUDGET_FRACTION_L0: float = 0.4
BUDGET_FRACTION_L1: float = 0.4
BUDGET_FRACTION_L2: float = 0.2

# Smart-survey default promotion fraction (40% of eligible promotions per tier)
DEFAULT_PROMOTION_FRACTION: float = 0.4
# Minimum promotions per tier if any eligible
MIN_PROMOTIONS_PER_TIER: int = 1

# Fidelity progression defaults (can be overridden in RunSpec)
DEFAULT_FIDELITY_SEEDS: dict[str, int] = {"L0": 1, "L1": 2, "L2": 5}
DEFAULT_FIDELITY_EPOCHS: dict[str, int] = {"L0": 1, "L1": 3, "L2": 10}

# Fidelity order for promotion logic
FIDELITY_ORDER: tuple[str, ...] = ("L0", "L1", "L2")

# Estimated cell costs for preview calculations (seconds per cell)
# Based on measured cell costs at each fidelity
ESTIMATED_CELL_COST_L0: int = 5  # ~5s per L0 cell (1 epoch, 1 seed)
ESTIMATED_CELL_COST_L1: int = 30  # ~30s per L1 cell (3 epochs, 2 seeds)
ESTIMATED_CELL_COST_L2: int = 300  # ~300s per L2 cell (10 epochs, 5 seeds)


def compute_budget_allocation(budget_seconds: int) -> dict[str, int]:
    """Compute budget allocation per fidelity tier.

    Args:
        budget_seconds: Total budget in seconds.

    Returns:
        Dict mapping fidelity -> allocated seconds.
    """
    return {
        "L0": int(budget_seconds * BUDGET_FRACTION_L0),
        "L1": int(budget_seconds * BUDGET_FRACTION_L1),
        "L2": int(budget_seconds * BUDGET_FRACTION_L2),
    }


def estimate_cell_counts(budget_seconds: int) -> dict[str, int]:
    """Estimate how many cells can be evaluated at each fidelity.

    Args:
        budget_seconds: Total budget in seconds.

    Returns:
        Dict mapping fidelity -> estimated cell count.
    """
    allocation = compute_budget_allocation(budget_seconds)
    return {
        "L0": max(1, allocation["L0"] // ESTIMATED_CELL_COST_L0),
        "L1": max(1, allocation["L1"] // ESTIMATED_CELL_COST_L1),
        "L2": max(1, allocation["L2"] // ESTIMATED_CELL_COST_L2),
    }


def estimate_promotions(
    l0_cells: int, l1_cells: int, promotion_fraction: float = DEFAULT_PROMOTION_FRACTION
) -> tuple[int, int]:
    """Estimate promotion counts between fidelity tiers.

    Args:
        l0_cells: Number of L0 cells screened.
        l1_cells: Number of L1 cells confirmed.
        promotion_fraction: Fraction of top cells to promote (default 0.4).

    Returns:
        Tuple of (L0->L1 promotions, L1->L2 promotions).
    """
    l0_l1_promos = max(MIN_PROMOTIONS_PER_TIER, int(l0_cells * promotion_fraction))
    l1_l2_promos = max(MIN_PROMOTIONS_PER_TIER, int(l1_cells * promotion_fraction))
    return l0_l1_promos, l1_l2_promos


def format_preview(hours: float) -> str:
    """Generate a formatted preview string for the smart-survey profile.

    Args:
        hours: Time budget in hours.

    Returns:
        Formatted preview string.
    """
    budget_seconds = int(hours * 3600)
    allocation = compute_budget_allocation(budget_seconds)
    cell_counts = estimate_cell_counts(budget_seconds)
    l0_l1_promos, l1_l2_promos = estimate_promotions(
        cell_counts["L0"], cell_counts["L1"]
    )

    lines = [
        "",
        f"📋 Smart Survey Preview ({hours}h budget):",
        "┌────────────────────────────────────────────────────────────┐",
        "│ Fidelity   Budget    Est. Cells   Promotes To              │",
        "├────────────────────────────────────────────────────────────┤",
        "│ L0 (screen)  {l0_budget:>5}s      ~{l0_cells:<4}          → L1: ~{l0_l1_promos:<4} │".format(
            l0_budget=allocation["L0"],
            l0_cells=cell_counts["L0"],
            l0_l1_promos=l0_l1_promos,
        ),
        "│ L1 (confirm) {l1_budget:>5}s      ~{l1_cells:<4}          → L2: ~{l1_l2_promos:<4} │".format(
            l1_budget=allocation["L1"],
            l1_cells=cell_counts["L1"],
            l1_l2_promos=l1_l2_promos,
        ),
        "│ L2 (deepen)  {l2_budget:>5}s      ~{l2_cells:<4}          (final)                 │".format(
            l2_budget=allocation["L2"], l2_cells=cell_counts["L2"]
        ),
        "└────────────────────────────────────────────────────────────┘",
        "",
        "Expected outcomes:",
        "  • Will screen ~{l0_cells} cells at L0 (1 epoch, 1 seed, CHEAP tasks)".format(
            l0_cells=cell_counts["L0"]
        ),
        f"  • Will promote ~{l0_l1_promos} cells to L1 (3 epochs, 2 seeds, CHEAP+MEDIUM tasks)",
        f"  • Will deepen ~{l1_l2_promos} cells to L2 (10 epochs, 5 seeds, ALL tasks)",
        "  • Top combos at L2 will have n_seeds=5 with CI reporting",
        "  • Multi-task: ≥3 tasks represented in top combos",
        "",
    ]
    return "\n".join(lines)


__all__ = [
    "BUDGET_FRACTION_L0",
    "BUDGET_FRACTION_L1",
    "BUDGET_FRACTION_L2",
    "DEFAULT_FIDELITY_EPOCHS",
    "DEFAULT_FIDELITY_SEEDS",
    "DEFAULT_PROMOTION_FRACTION",
    "ESTIMATED_CELL_COST_L0",
    "ESTIMATED_CELL_COST_L1",
    "ESTIMATED_CELL_COST_L2",
    "FIDELITY_ORDER",
    "MIN_PROMOTIONS_PER_TIER",
    "compute_budget_allocation",
    "estimate_cell_counts",
    "estimate_promotions",
    "format_preview",
]
