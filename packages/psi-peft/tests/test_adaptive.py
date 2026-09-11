"""Conflict-adaptive variant: self-switching decay without boundaries."""

from __future__ import annotations

import torch
from psi_peft.adaptive import AdaptivePsiReadout
from psi_peft.metrics import Readout, SyntheticTask

FEATURE_DIM, NUM_CLASSES = 16, 3


def _warm(readout: Readout, task: SyntheticTask, episodes: int = 8) -> None:
    for _ in range(episodes):
        h, y = task.batch(64)
        readout.update(h, y)


def test_warmup_counts_as_conflict() -> None:
    gen = torch.Generator().manual_seed(0)
    task = SyntheticTask(gen, FEATURE_DIM, NUM_CLASSES)
    readout = AdaptivePsiReadout(FEATURE_DIM, NUM_CLASSES)
    readout.update(*task.batch(64))
    assert readout.last_agreement is None
    assert readout.last_rho == readout.forget_decay


def test_steady_phase_stops_forgetting() -> None:
    gen = torch.Generator().manual_seed(1)
    task = SyntheticTask(gen, FEATURE_DIM, NUM_CLASSES)
    readout = AdaptivePsiReadout(FEATURE_DIM, NUM_CLASSES)
    _warm(readout, task)
    h, y = task.batch(64)
    readout.update(h, y)
    assert readout.last_agreement is not None
    assert readout.last_agreement > readout.conflict_threshold
    assert readout.last_rho == 1.0


def test_flip_triggers_forgetting_within_two_episodes() -> None:
    gen = torch.Generator().manual_seed(2)
    task = SyntheticTask(gen, FEATURE_DIM, NUM_CLASSES)
    readout = AdaptivePsiReadout(FEATURE_DIM, NUM_CLASSES)
    _warm(readout, task)
    task.flip()
    lag = None
    for i in range(1, 3):
        h, y = task.batch(64)
        readout.update(h, y)
        if readout.last_rho == readout.forget_decay:
            lag = i
            break
    assert lag is not None and lag <= 2
