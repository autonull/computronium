"""CUDA-stream double-buffering: the epoch it produces must be the epoch claimed.

``SystemTrainerConfig.async_dataloading`` prefetches the next batch on its own
stream so its H2D copy overlaps the current batch's forward/backward. That is
only free if the overlap changes nothing else: same batches, same order, same
number of steps, same metrics as the synchronous path. This asserts that
against a reference run, so an optimization that silently drops the last batch
— which a prefetch loop can do easily, because its exhaustion is a ``None``
sentinel rather than a ``StopIteration`` — fails here instead of showing up as
a quietly worse model.

Every test here needs a real device: the code under test is the stream
bookkeeping, and a mocked stream is the absence of the thing being tested.
"""

from __future__ import annotations

import pytest
import torch

from computronium.core.rules import rule_system
from computronium.core.system_trainer import SystemTrainer, SystemTrainerConfig

CUDA = pytest.mark.skipif(not torch.cuda.is_available(), reason="needs a CUDA device")

_BATCHES = 5
_BATCH = 8
_DIM = 6
_OUT = 3


class _Batches:
    """A fixed list of ``(inputs, targets)`` pairs, re-iterable per epoch."""

    def __init__(self, n: int = _BATCHES) -> None:
        generator = torch.Generator().manual_seed(7)
        self._pairs = [
            (
                torch.randn(_BATCH, _DIM, generator=generator),
                torch.randint(0, _OUT, (_BATCH,), generator=generator),
            )
            for _ in range(n)
        ]

    def __iter__(self):
        return iter(self._pairs)

    def __len__(self) -> int:
        return len(self._pairs)


def _trainer(*, async_dataloading: bool, batches: _Batches) -> SystemTrainer:
    torch.manual_seed(0)
    system = rule_system("ep", _DIM, _OUT, hidden_dims=(8,), device="cuda")
    return SystemTrainer(
        system=system,
        config=SystemTrainerConfig(
            max_epochs=1,
            device="cuda",
            seed=0,
            async_dataloading=async_dataloading,
        ),
        train_data=batches,
    )


@CUDA
def test_the_async_epoch_matches_the_synchronous_one() -> None:
    """Double-buffering is an optimization, so it may not move any number."""
    sync = _trainer(async_dataloading=False, batches=_Batches()).train_epoch()
    async_ = _trainer(async_dataloading=True, batches=_Batches()).train_epoch()

    for key in ("train_loss", "train_acc", "train_energy"):
        assert async_[key] == pytest.approx(sync[key], rel=1e-5), key
    assert async_["global_step"] == sync["global_step"]


@CUDA
def test_a_short_stream_ends_the_epoch_instead_of_raising() -> None:
    """A prefetch loop learns of exhaustion from a sentinel, not an exception.

    ``max_batches`` exceeds the stream length here, so the async path reaches
    its end mid-epoch. If it treats "no next batch" as "no break", the epoch
    either trains on ``None`` or spins.
    """
    trainer = _trainer(async_dataloading=True, batches=_Batches(n=3))
    record = trainer.train_epoch()

    assert trainer.global_step == 3
    assert record["global_step"] == 3


@CUDA
def test_the_prefetched_batch_is_the_next_batch_not_the_same_one() -> None:
    """Off-by-one in the buffer is the failure this whole mechanism can have.

    Two prefetch bugs produce a plausible epoch: consuming the batch about to
    be prefetched (so batch *n* trains twice and batch *N-1* never trains), and
    never advancing the buffer (so one batch trains *N* times). Both agree with
    the synchronous path on step count, so they are checked against the inputs
    each batch actually saw.
    """
    batches = _Batches()
    seen: list[torch.Tensor] = []

    trainer = _trainer(async_dataloading=True, batches=batches)
    inner = trainer.system

    class _Spy:
        geometry = inner.geometry

        def train_step(self, x, y):
            seen.append(x.detach().cpu().clone())
            return inner.train_step(x, y)

    trainer.system = _Spy()  # type: ignore[assignment]
    trainer.train_epoch()

    expected = [x.cuda() for x, _ in batches]
    assert len(seen) == _BATCHES
    for got, want in zip(seen, expected, strict=True):
        torch.testing.assert_close(got, want.cpu())


@CUDA
def test_async_dataloading_is_inert_on_a_cpu_run() -> None:
    """The flag names CUDA streams; on CPU it must not reach for one."""
    torch.manual_seed(0)
    system = rule_system("ep", _DIM, _OUT, hidden_dims=(8,), device="cpu")
    trainer = SystemTrainer(
        system=system,
        config=SystemTrainerConfig(
            max_epochs=1, device="cpu", seed=0, async_dataloading=True
        ),
        train_data=_Batches(),
    )
    record = trainer.train_epoch()

    assert record["global_step"] == _BATCHES
