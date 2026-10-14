"""Deterministic seed hierarchy: master → cycle → cell.

Provides SeedContext for reproducible seed derivation across the entire
experiment lifecycle. A cell's identity includes (master, cycle, cell)
making From-Scratch tests and discovery/confirmation separation meaningful.
"""

from __future__ import annotations

import hashlib
import random
from dataclasses import dataclass

import numpy as np
import torch


@dataclass(frozen=True, slots=True)
class SeedContext:
    """Deterministic seed hierarchy for the entire experiment.

    Structure:
    - master_seed: Single seed for the entire experiment (user-provided or random)
    - cycle_seed: Derived per cycle from master_seed
    - cell_seed: Derived per cell from cycle_seed + cell identity

    This ensures:
    - Two runs with same master_seed produce identical cell seeds
    - From-Scratch replay reproduces exact same seed sequence
    - Discovery/confirmation seed separation is enforced
    """

    master_seed: int

    def cycle_seed(self, cycle_index: int) -> int:
        """Derive cycle seed from master seed and cycle index."""
        return self._derive_seed(f"cycle:{cycle_index}")

    def cell_seed(
        self,
        cycle_index: int,
        cell_index: int,
        cell_coordinate: str | None = None,
    ) -> int:
        """Derive cell seed from cycle seed and cell identity.

        Args:
            cycle_index: The cycle this cell belongs to
            cell_index: Sequential index of cell within cycle
            cell_coordinate: Optional coordinate string for coordinate-based derivation
        """
        if cell_coordinate:
            return self._derive_seed(f"cell:{cycle_index}:{cell_coordinate}")
        return self._derive_seed(f"cell:{cycle_index}:{cell_index}")

    def seed_plan(
        self, cycle_index: int, cell_count: int, n_seeds_per_cell: int
    ) -> list[list[int]]:
        """Generate complete seed plan for a cycle.

        Returns:
            List of seed lists, one per cell, each containing n_seeds_per_cell seeds.
            Outer index is cell_index, inner list contains seeds for that cell's replicates.
        """
        cycle_s = self.cycle_seed(cycle_index)
        cell_seeds = []
        for cell_idx in range(cell_count):
            cell_base = self._derive_from_base(cycle_s, f"cell:{cell_idx}")
            seeds = [
                self._derive_from_base(cell_base, f"replicate:{rep_idx}")
                for rep_idx in range(n_seeds_per_cell)
            ]
            cell_seeds.append(seeds)
        return cell_seeds

    def discovery_seeds(self, cycle_index: int, cell_count: int) -> list[int]:
        """Seeds for discovery phase (first N seeds of each cell).

        These seeds are used for initial exploration and proposal selection.
        They MUST NOT be reused for confirmation.
        """
        return [
            self._derive_seed(f"discovery:{cycle_index}:{cell_idx}")
            for cell_idx in range(cell_count)
        ]

    def confirmation_seeds(
        self, cycle_index: int, cell_count: int, n_confirm: int
    ) -> list[list[int]]:
        """Seeds for confirmation phase (fresh seeds, never used in discovery).

        These seeds are used for L2 replay verification and must be
        completely disjoint from discovery seeds.
        """
        confirm_seeds = []
        for cell_idx in range(cell_count):
            cell_base = self._derive_seed(f"confirm:{cycle_index}:{cell_idx}")
            seeds = [
                self._derive_from_base(cell_base, f"replicate:{rep_idx}")
                for rep_idx in range(n_confirm)
            ]
            confirm_seeds.append(seeds)
        return confirm_seeds

    def _derive_seed(self, context: str) -> int:
        """Derive a deterministic seed from master_seed + context string."""
        combined = f"{self.master_seed}:{context}"
        hash_bytes = hashlib.sha256(combined.encode()).digest()
        # Use first 8 bytes as 64-bit integer
        return int.from_bytes(hash_bytes[:8], "little") % (2**31 - 1)

    def _derive_from_base(self, base_seed: int, context: str) -> int:
        """Derive a seed from a base seed + context."""
        combined = f"{base_seed}:{context}"
        hash_bytes = hashlib.sha256(combined.encode()).digest()
        return int.from_bytes(hash_bytes[:8], "little") % (2**31 - 1)

    def set_global_seeds(self, seed: int | None = None) -> None:
        """Set global random seeds for Python, NumPy, PyTorch.

        Call this at the start of each cell execution with the cell's seed.
        """
        s = seed if seed is not None else self.master_seed
        random.seed(s)
        np.random.seed(s)
        torch.manual_seed(s)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(s)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False
        torch.use_deterministic_algorithms(True)


@dataclass(frozen=True, slots=True)
class CellSeedPlan:
    """Complete seed plan for a single cell across all its replicates."""

    cell_key: str
    cycle_index: int
    cell_index: int
    discovery_seeds: list[int]
    confirmation_seeds: list[list[int]]  # Per-replicate confirmation seeds

    @property
    def all_seeds(self) -> list[int]:
        """All seeds for this cell (discovery + all confirmation)."""
        all_s = list(self.discovery_seeds)
        for rep_seeds in self.confirmation_seeds:
            all_s.extend(rep_seeds)
        return all_s


class SeedContextManager:
    """Manages SeedContext across experiment lifecycle."""

    def __init__(self, master_seed: int | None = None) -> None:
        if master_seed is None:
            # Generate from system entropy if not provided
            master_seed = random.SystemRandom().randint(0, 2**31 - 1)
        self._context = SeedContext(master_seed=master_seed)
        self._current_cycle = 0
        self._cell_plans: dict[str, CellSeedPlan] = {}

    @property
    def master_seed(self) -> int:
        return self._context.master_seed

    @property
    def current_cycle(self) -> int:
        return self._current_cycle

    def next_cycle(self) -> int:
        """Advance to next cycle and return its index."""
        self._current_cycle += 1
        return self._current_cycle - 1

    def get_cycle_seed(self, cycle_index: int | None = None) -> int:
        """Get seed for a cycle."""
        idx = cycle_index if cycle_index is not None else self._current_cycle
        return self._context.cycle_seed(idx)

    def plan_cell_seeds(
        self,
        cell_key: str,
        cell_index: int,
        n_discovery: int = 1,
        n_confirmation: int = 5,
    ) -> CellSeedPlan:
        """Plan all seeds for a cell in the current cycle."""
        cycle_idx = self._current_cycle
        discovery = [
            self._context._derive_seed(f"discovery:{cycle_idx}:{cell_index}")
            for _ in range(n_discovery)
        ]
        confirmation = []
        for rep in range(n_confirmation):
            rep_base = self._context._derive_seed(
                f"confirm:{cycle_idx}:{cell_index}:rep:{rep}"
            )
            confirmation.append([rep_base])

        plan = CellSeedPlan(
            cell_key=cell_key,
            cycle_index=cycle_idx,
            cell_index=cell_index,
            discovery_seeds=discovery,
            confirmation_seeds=confirmation,
        )
        self._cell_plans[cell_key] = plan
        return plan

    def get_cell_plan(self, cell_key: str) -> CellSeedPlan | None:
        """Retrieve a previously planned cell seed plan."""
        return self._cell_plans.get(cell_key)

    def set_cell_seeds(self, cell_key: str) -> int:
        """Set global seeds for a cell's first discovery seed.

        Returns the seed that was set.
        """
        plan = self._cell_plans.get(cell_key)
        if plan is None:
            raise ValueError(f"No seed plan for cell {cell_key}")
        seed = (
            plan.discovery_seeds[0]
            if plan.discovery_seeds
            else self._context.cycle_seed(plan.cycle_index)
        )
        self._context.set_global_seeds(seed)
        return seed


def create_seed_context(master_seed: int | None = None) -> SeedContext:
    """Factory for SeedContext."""
    return SeedContext(
        master_seed=master_seed or random.SystemRandom().randint(0, 2**31 - 1)
    )


__all__ = [
    "CellSeedPlan",
    "SeedContext",
    "SeedContextManager",
    "create_seed_context",
]
