"""TODO66 §2.9: an ablation table is a comparison or it is not printed.

Measured on the flagship `quick-verify` run, the per-axis "Credit Ablation"
table reported `gradient` 0.094 against `pepita` 0.528 — because the six-axis
sweep gave each credit value its own geometry, optimizer and hidden size. A
confounded table is the project's most quotable artifact and its most damaging
one; the lock is that a table appears only when the other five axes are held
fixed, every row carries ``n``/``std``, and any arm at chance says so.
"""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any

from computronium.experiment.surface.report import (
    _ablation_section,
    chance_level,
    contrast_groups,
)

_BASE: dict[str, Any] = {
    "substrate": "digital",
    "geometry": "feedforward",
    "dynamics": "instantaneous",
    "plasticity": "null",
    "update": "adam",
}


def _record(credit: str, val_acc: float, **overrides: Any) -> SimpleNamespace:
    axes = {**_BASE, "credit": credit, **overrides}
    return SimpleNamespace(
        **axes,
        params={"hidden_dim": 32},
        payload={"val_acc": val_acc},
        schedule=SimpleNamespace(task_id="digits"),
    )


class _Store:
    def __init__(self, records: list[SimpleNamespace]) -> None:
        self._records = records

    def query_records(self, *, run_id: str | None = None) -> list[SimpleNamespace]:
        return list(self._records)


def test_a_confounded_run_produces_no_ablation_table() -> None:
    records = [
        _record("gradient", 0.09, hidden_dim=8),
        _record("pepita", 0.53, update="adam"),
        _record("local_goodness", 0.39, dynamics="lazy"),
    ]
    # Every cell differs on some other axis, so no group shares the other five.
    records[0].params = {"hidden_dim": 8}
    records[2].params = {"hidden_dim": 64}
    assert contrast_groups(records, "credit") == []

    text = "\n".join(_ablation_section(_Store(records), "run"))
    assert "no ablation table is reported" in text
    assert "gradient" in text  # the raw per-cell list still appears


def test_a_shared_five_axis_group_produces_a_flagged_table() -> None:
    records = [
        _record("gradient", 0.80),
        _record("random_projections", 0.09),
        _record("pepita", 0.75),
    ]
    groups = contrast_groups(records, "credit")
    assert len(groups) == 1, "three cells sharing five axes are one contrast group"

    text = "\n".join(_ablation_section(_Store(records), "run"))
    assert "Credit Ablation" in text
    for line in text.splitlines():
        if line.strip().startswith(("gradient:", "random_projections:", "pepita:")):
            assert "n=" in line and "std=" in line
    assert "random_projections: mean=0.09" in text
    assert "at chance" in text


def test_chance_level_is_read_from_the_task_output_dim() -> None:
    assert chance_level("digits", "val_acc") == 0.1
    assert chance_level("digits", "walltime_total") is None
