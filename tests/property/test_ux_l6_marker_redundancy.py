"""UX-L6: marker redundancy — outcome badges stay distinguishable without color.

Static lock (a): every OutcomeBadge style carries a unique (icon, label) pair,
and icons are pairwise distinct — grayscale-proof by construction. The
behavioral grayscale pair lives in tests/ui/test_ux_l6_grayscale.py (C6,
no committed pixel baselines per user directive 2026-09-23).
"""

from __future__ import annotations


def test_every_outcome_badge_has_a_style() -> None:
    from computronium.visualization.live_atlas import _OUTCOME_STYLES, OutcomeBadge

    assert set(_OUTCOME_STYLES) == set(OutcomeBadge), "style table covers every badge"


def test_outcome_style_icon_label_pairs_unique() -> None:
    """Shape/label redundancy: no two badges share an (icon, label) pair."""
    from computronium.visualization.live_atlas import _OUTCOME_STYLES

    pairs = [(style.icon, style.label) for style in _OUTCOME_STYLES.values()]
    assert len(set(pairs)) == len(pairs), f"duplicate (icon, label) pairs: {pairs}"


def test_outcome_labels_unique() -> None:
    from computronium.visualization.live_atlas import _OUTCOME_STYLES

    labels = [style.label for style in _OUTCOME_STYLES.values()]
    assert len(set(labels)) == len(labels), f"duplicate labels: {labels}"


def test_outcome_icons_unique() -> None:
    """Icon-only redundancy: badges remain distinct in pure grayscale."""
    from computronium.visualization.live_atlas import _OUTCOME_STYLES

    icons = [style.icon for style in _OUTCOME_STYLES.values()]
    assert len(set(icons)) == len(icons), f"duplicate icons: {icons}"
