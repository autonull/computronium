"""Benchmark Contributions — Standard tasks, reference results, leaderboards.

Provides a framework for community-contributed benchmarks with:
- Standardized task definitions with reference implementations
- Automated comparison against reference baselines
- Leaderboard generation and tracking
"""

from __future__ import annotations

from computronium.benchmarks.contributions.core.registry import (
    BenchmarkContribution,
    BenchmarkTask,
    ContributionRegistry,
    Leaderboard,
    LeaderboardEntry,
    ReferenceResult,
    contribution_registry,
)

__all__ = [
    "BenchmarkContribution",
    "BenchmarkTask",
    "ContributionRegistry",
    "Leaderboard",
    "LeaderboardEntry",
    "ReferenceResult",
    "contribution_registry",
]
