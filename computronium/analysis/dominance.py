"""Pareto dominance and non-dominated-front selection.

Renderer-free by construction. The domain asks "which rows are on the front";
the view asks "draw the front". Those are different questions, and when the
domain imports the view's copy, the front-selection rule becomes a property of
a charting module — which is where nobody looks for an optimization rule.

``compute_pareto_frontier`` in :mod:`computronium.analysis.pareto` solves the
same problem over ``ParetoPoint`` records; this module works directly on a
DataFrame of objective columns, which is what the atlas and the campaign
readers actually hold.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    import pandas as pd

    from computronium.autoscientist.objectives import ObjectiveSpec

# Boolean-work budget per broadcast: chunk_rows × n ≤ this (≈8 MB per temp).
_DOMINANCE_CHUNK = 8_000_000


def _dominated_2d(oriented: np.ndarray) -> np.ndarray:
    """Dominance mask for two all-maximize objectives via sort + sweep (O(n log n)).

    Points are processed best-first on axis 0; a point survives iff its axis-1
    value beats every earlier point, ties on both axes (exact duplicates)
    survive together — matching the strict pairwise definition.
    """
    o0 = oriented[:, 0]
    o1 = oriented[:, 1]
    order = np.lexsort((-o1, -o0))  # o0 desc, then o1 desc
    dominated = np.zeros(len(o0), dtype=bool)
    max_o1 = -np.inf
    o0_at_max_o1 = -np.inf
    for idx in order:
        v0, v1 = o0[idx], o1[idx]
        if v1 > max_o1:
            max_o1 = v1
            o0_at_max_o1 = v0
        elif v1 < max_o1 or v0 < o0_at_max_o1:
            dominated[idx] = True
        # v1 == max_o1 and v0 == o0_at_max_o1 → exact duplicate of a survivor
    return dominated


def _dominated_vectorized(oriented: np.ndarray) -> np.ndarray:
    """Dominance mask via chunked broadcast; preserves NaN-as-equal semantics.

    A NaN objective neither fails the >= test nor contributes strictness —
    matching the original pairwise loop (`NaN < x` and `NaN > x` are both
    False). Chunks bound memory at ``_CHUNK × n`` booleans for large n.
    """
    n = len(oriented)
    dominated = np.zeros(n, dtype=bool)
    chunk = max(1, min(1024, _DOMINANCE_CHUNK // max(n, 1)))
    for start in range(0, n, chunk):
        block = oriented[start : start + chunk]  # (c, d)
        nan_block = np.isnan(block)[:, None, :]
        nan_all = np.isnan(oriented)[None, :, :]
        ge = (block[:, None, :] <= oriented[None, :, :]) | nan_block | nan_all
        ge_all = ge.all(axis=2)
        strict = (
            (block[:, None, :] < oriented[None, :, :]) & ~nan_block & ~nan_all
        ).any(axis=2)
        dom = ge_all & strict
        rows = np.arange(start, start + len(block))
        dom[np.arange(len(block)), rows] = False  # exclude self
        dominated[start : start + len(block)] = dom.any(axis=1)
    return dominated


def pareto_top(
    df: pd.DataFrame,
    k: int = 3,
    objectives: tuple[ObjectiveSpec, ...] = (),
) -> pd.DataFrame:
    """Non-dominated cells on configurable objectives.

    Args:
        df: DataFrame with objective columns
        k: Maximum number of front cells to return
        objectives: Tuple of ObjectiveSpec defining the optimization. Empty
            means "no objective set configured", which yields no front rather
            than the whole frame — callers pass the resolved set explicitly.
    """
    from computronium.autoscientist.objectives import DEFAULT_OBJECTIVES

    objectives = objectives or DEFAULT_OBJECTIVES
    if df.empty or not objectives:
        return df

    obj_names = [o.name.value for o in objectives]
    directions = [o.direction for o in objectives]

    # Unknown objectives fail loudly: silently returning the unfiltered
    # frame rendered fake fronts.
    missing = [name for name in obj_names if name not in df.columns]
    if missing:
        raise ValueError(
            f"Unknown/unsupported objectives {missing}; "
            f"available columns: {sorted(df.columns)}"
        )

    pts = df[obj_names].to_numpy(dtype=float)
    signs = np.where([d == "maximize" for d in directions], 1.0, -1.0)
    oriented = pts * signs  # larger is better on every axis
    has_nan = bool(np.isnan(oriented).any())

    if len(obj_names) == 2 and not has_nan:
        dominated = _dominated_2d(oriented)
    else:
        dominated = _dominated_vectorized(oriented)

    front = df.loc[np.flatnonzero(~dominated)].sort_values(
        obj_names[0], ascending=(directions[0] == "minimize")
    )
    return front.head(k)
