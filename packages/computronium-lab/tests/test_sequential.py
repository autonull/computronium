"""TODO23 sequence tier: synthetic sequence tasks + BPTT training + campaign."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
import torch
from computronium_lab import (
    SEQUENCE_TASKS,
    Lab,
    sequence_campaign,
    sequence_task,
    train_sequence,
)
from computronium_lab.recipes import build_ntm_sequence

if TYPE_CHECKING:
    from pathlib import Path


def test_sequence_task_shapes() -> None:
    for name in SEQUENCE_TASKS:
        x, y = sequence_task(name, batch_size=16, seq_len=8, input_dim=8, seed=0)
        assert x.shape == (16, 8, 8)
        assert y.shape == (16,)
        assert set(y.unique().tolist()) <= {0, 1}
    with pytest.raises(ValueError, match="unknown sequence task"):
        sequence_task("nonexistent")


def test_train_sequence_requires_episode_api() -> None:
    from types import SimpleNamespace

    with pytest.raises(TypeError, match="episode"):
        train_sequence(SimpleNamespace(geometry=object()), "parity", epochs=1)


def test_train_sequence_learns_last_symbol() -> None:
    """Measured operating point (TODO23 §12): 0.80 @ 60ep, 1 seed."""
    result = train_sequence(build_ntm_sequence(), "last_symbol", epochs=60, seed=0)
    assert result.accuracy > result.chance + 0.15
    assert result.history[-1]["loss"] < result.history[0]["loss"]


def test_lab_train_sequence_entrypoint() -> None:
    lab = Lab(seed=0)
    result = lab.train_sequence(build_ntm_sequence(), "threshold", epochs=5)
    assert 0.0 <= result.accuracy <= 1.0
    assert result.walltime_s > 0.0


def test_sequence_campaign_certifies(tmp_path: Path) -> None:
    """§6-governed sequence campaign on the measured operating point."""
    ledger = tmp_path / "ledger.db"
    lab = Lab(seed=0, record_ledger=str(ledger))
    report = sequence_campaign(
        lab,
        build_ntm_sequence,
        "last_symbol",
        predicted_accuracy=0.92,
        seeds=(0, 1, 2),
        epochs=120,
        out_dir=str(tmp_path / "exports"),
    )
    assert report.reproduction, report.summary()
    assert report.deployability
    assert report.certified
    assert report.matched_control
    assert report.control_accuracy is not None and report.control_accuracy < 0.6

    from computronium_lab.campaign import ledger_audit

    audit = ledger_audit(ledger)
    assert audit["clean"], audit


def test_sequence_campaign_records_failure(tmp_path: Path) -> None:
    """An unreproduced corpus records the negative result (§6)."""
    ledger = tmp_path / "ledger.db"
    lab = Lab(seed=0, record_ledger=str(ledger))
    # parity at this budget sits at chance → reproduction must fail
    report = sequence_campaign(
        lab,
        build_ntm_sequence,
        "parity",
        predicted_accuracy=0.92,
        seeds=(0,),
        epochs=5,
    )
    assert not report.reproduction
    assert not report.certified


def test_ntm_sequence_screened_by_validate() -> None:
    """Catalog row's construction passes the hard SystemConfig screen."""
    from computronium_lab.synthesis.spec import Constraints, ProblemSpec

    spec = ProblemSpec(
        task="sequence_classification",
        dataset="synthetic",
        constraints=Constraints(),
        input_dim=8,
        num_classes=2,
    )
    from computronium_lab.synthesis.catalog import CATALOG
    from computronium_lab.synthesis.engine import screen_config

    cand = next(c for c in CATALOG if c.name == "ntm_sequence")
    screen_config(cand, spec)
    system = cand.build(spec)
    assert system is not None


def test_psi_program_composes_task_sequences() -> None:
    """E4 over NTM: a ψ-program acquires two sequence tasks on one live ψ
    state; theta stays bitwise frozen across the whole program."""
    from computronium_lab.adaptation import PsiProgram, PsiStep

    system = build_ntm_sequence()
    train_sequence(system, "last_symbol", epochs=20, seed=0)

    def stream(label_rule):
        def gen():
            for _ in range(3):
                x = torch.randn(16, 8, 8)
                yield x, label_rule(x)

        return gen()

    program = PsiProgram(PsiStep("last_symbol", "temporal", 2)) + PsiProgram(
        PsiStep("threshold", "conflict_adaptive", 2)
    )
    data = {
        "last_symbol": stream(lambda x: (x[:, -1].mean(-1) > 0).long()),
        "threshold": stream(lambda x: (x.sum(dim=(1, 2)) > 0).long()),
    }
    result, steps = program.run(system, data)
    assert len(steps) == 2
    assert all(r.theta.bitwise_invariant for r in steps)
    assert result.theta.bitwise_invariant
    assert result.psi_updated
