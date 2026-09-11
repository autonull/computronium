"""Buffered variant: interval refit, drift-triggered forgetting, speed."""

from __future__ import annotations

import torch
from psi_peft.buffered import BufferedPsiReadout
from psi_peft.metrics import Readout, SyntheticTask

FEATURE_DIM, NUM_CLASSES = 16, 3


def _run(readout: Readout, task: SyntheticTask, episodes: int = 10) -> float:
    for _ in range(episodes):
        h, y = task.batch(64)
        readout.update(h, y)
    h, y = task.batch(512)
    return float((readout.forward(h).argmax(-1) == y).float().mean().item())


def test_refit_interval_solves_less_often() -> None:
    readout = BufferedPsiReadout(
        FEATURE_DIM, NUM_CLASSES, buffer_size=8, refit_interval=4
    )
    gen = torch.Generator().manual_seed(0)
    task = SyntheticTask(gen, FEATURE_DIM, NUM_CLASSES)
    solves = 0
    original = readout.refit

    def counting_refit() -> None:
        nonlocal solves
        solves += 1
        original()

    readout.refit = counting_refit  # type: ignore[method-assign]
    for _ in range(10):
        h, y = task.batch(64)
        readout.update(h, y)
    assert solves <= 4  # interval refits only


def test_drift_clears_stale_episodes() -> None:
    gen = torch.Generator().manual_seed(1)
    task = SyntheticTask(gen, FEATURE_DIM, NUM_CLASSES)
    readout = BufferedPsiReadout(
        FEATURE_DIM, NUM_CLASSES, buffer_size=8, drift_threshold=0.6
    )
    for _ in range(10):
        readout.update(*task.batch(64))
    task.flip()
    readout.update(*task.batch(64))
    assert len(readout.buffer) == 1


def test_buffered_tracks_conflicting_task() -> None:
    gen = torch.Generator().manual_seed(2)
    task = SyntheticTask(gen, FEATURE_DIM, NUM_CLASSES)
    readout = BufferedPsiReadout(
        FEATURE_DIM, NUM_CLASSES, buffer_size=8, refit_interval=2, drift_threshold=0.6
    )
    for _ in range(10):
        readout.update(*task.batch(64))
    task.flip()
    for _ in range(8):
        readout.update(*task.batch(64))
    h, y = task.batch(512)
    acc = (readout.forward(h).argmax(-1) == y).float().mean().item()
    assert acc > 0.45  # chance is 0.333


def test_refit_count_bounded() -> None:
    gen = torch.Generator().manual_seed(3)
    task = SyntheticTask(gen, FEATURE_DIM, NUM_CLASSES)
    readout = BufferedPsiReadout(FEATURE_DIM, NUM_CLASSES, refit_interval=8)
    for _ in range(64):
        readout.update(*task.batch(64))
    assert readout.trace_steps == 64
