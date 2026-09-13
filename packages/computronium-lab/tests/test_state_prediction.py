"""TODO23 state-prediction tier: grid transition task + NCA campaign."""

from __future__ import annotations

from types import SimpleNamespace
from typing import TYPE_CHECKING

import pytest
import torch
from computronium_lab import Lab
from computronium_lab.recipes import build_nca_predictor, build_recipe
from computronium_lab.state_prediction import (
    grid_transition_task,
    state_prediction_campaign,
    train_state_prediction,
)
from computronium_lab.synthesis.catalog import CATALOG

if TYPE_CHECKING:
    from pathlib import Path


def test_grid_transition_task_shapes() -> None:
    task = grid_transition_task(0)
    assert task.train_states.shape == (256, 4, 10, 10)
    assert task.val_states.shape == (64, 4, 10, 10)
    again = grid_transition_task(0)
    assert torch.equal(task.train_next, again.train_next)


def test_train_state_prediction_learns_rollout() -> None:
    """k=3 rollout map is learnable and non-degenerate (one-step is not)."""
    task = grid_transition_task(0)
    result = train_state_prediction(
        build_recipe("nca_predictor"), task, epochs=100, seed=0
    )
    assert result.cell_accuracy >= 0.9
    assert 0.0 <= result.mse < 0.1
    assert result.chance == 0.25


def test_train_state_prediction_requires_nca() -> None:
    task = grid_transition_task(0)
    with pytest.raises(TypeError, match="composed ontology System"):
        train_state_prediction(object(), task)
    with pytest.raises(TypeError, match="NCA geometry"):
        train_state_prediction(SimpleNamespace(geometry=object()), task)


def test_nca_predictor_screened_by_validate() -> None:
    cand = next(c for c in CATALOG if c.name == "nca_predictor")
    assert cand.config_builder is not None
    for substrate in ("digital", "memristive"):
        cfg = cand.config_builder(substrate, "float32")
        cfg.validate()


def test_state_prediction_campaign_certifies(tmp_path: Path) -> None:
    """§6-governed campaign on the measured operating point (TODO23 §12)."""
    from computronium_lab.campaign import ledger_audit

    cand = next(c for c in CATALOG if c.name == "nca_predictor")
    lab = Lab(seed=0, record_ledger=str(tmp_path / "ledger.db"))
    report = state_prediction_campaign(
        lab,
        build_nca_predictor,
        predicted_accuracy=cand.pareto.accuracy,
        seeds=(0, 1, 2),
        epochs=100,
        out_dir=str(tmp_path / "exports"),
    )
    assert report.reproduction, report.summary()
    assert report.matched_control
    assert report.deployability
    assert report.certified
    audit = ledger_audit(str(lab.record_ledger))
    assert audit["clean"], audit


def test_state_prediction_campaign_records_failure(tmp_path: Path) -> None:
    """An impossible reproduction bar is recorded, not raised (§6)."""
    lab = Lab(seed=0, record_ledger=str(tmp_path / "ledger.db"))
    report = state_prediction_campaign(
        lab,
        build_nca_predictor,
        predicted_accuracy=1.2,
        seeds=(0,),
        epochs=100,
    )
    assert not report.reproduction
    assert not report.certified
