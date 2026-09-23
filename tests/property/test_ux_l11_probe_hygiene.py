"""UX-L11: probe batches never touch production training data (L4).

Forked-copy hygiene is structural — ``ProbeBatch`` cannot be constructed
in a non-forked state — and the panel copy discloses it. Listed in
GAME.todo.md §6; cited by ``ProbeAnalytics.expert_explanation``.
"""

from __future__ import annotations

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from computronium.ui.components.probe_analytics import ProbeAnalytics, ProbeBatch

_batches = st.builds(
    ProbeBatch,
    batch_id=st.text(min_size=1, max_size=16),
    timestamp=st.floats(min_value=0.0, max_value=1e10, allow_nan=False),
    current_slope=st.floats(min_value=-10.0, max_value=10.0, allow_nan=False),
    proposed_slope=st.floats(min_value=-10.0, max_value=10.0, allow_nan=False),
    accepted=st.booleans(),
    statistical_significance=st.floats(min_value=0.0, max_value=1.0),
)


@settings(max_examples=25, deadline=None)
@given(batch=_batches)
def test_ux_l11_batches_are_always_forked(batch: ProbeBatch) -> None:
    assert batch.forked_copy is True


def test_ux_l11_non_forked_construction_rejected() -> None:
    with pytest.raises(ValueError, match="forked_copy"):
        ProbeBatch(
            batch_id="x",
            timestamp=0.0,
            current_slope=0.0,
            proposed_slope=0.0,
            accepted=False,
            statistical_significance=1.0,
            forked_copy=False,
        )


@settings(max_examples=25, deadline=None)
@given(batches=st.lists(_batches, max_size=8))
def test_ux_l11_panel_preserves_hygiene(batches: list[ProbeBatch]) -> None:
    panel = ProbeAnalytics(batches=list(batches))
    assert all(b.forked_copy is True for b in panel.batches)
    panel.set_batches(list(batches))
    assert all(b.forked_copy is True for b in panel.batches)


def test_ux_l11_copy_discloses_forked_copy() -> None:
    panel = ProbeAnalytics()
    assert "forked copy" in panel.plain_explanation
    assert "forked-copy hygiene" in panel.expert_explanation
