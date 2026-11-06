"""The single settle-loop driver.

Ten hand-written ``for step in range(config.max_steps)`` loops across six
dynamics classes carried twenty-four distinct convergence-check sites. The
dead-early-stop defect of ``ff6528fb`` existed in four of those copies at
once: not four mistakes, but one copy-paste plus a flaw that travelled with
it. This module makes the control flow writeable once.

What the driver owns — the part that was duplicated and broke:

* horizon accounting: iterations run until the observer stops them or
  ``max_steps`` is reached, and the executed count is returned;
* the ordering that made the defect possible: ``advance`` first, horizon
  bookkeeping second, observer last. A step is *executed* before anything
  may stop the loop, so no flag can be consulted in place of the step
  itself.

What the driver deliberately does not own: the convergence predicate and
the scalar a telemetry consumer sees. Those are per-dynamics science.
Parameterising them here is how a "one driver" grows eleven flag
combinations and relocates complexity instead of removing it — the risk
stated in ``TODO34.md`` §5.1.
"""

from collections.abc import Callable, Iterable
from typing import TYPE_CHECKING, TypeVar

if TYPE_CHECKING:
    import torch
    from torch import Tensor

type SettleAdvance = Callable[[int], None]
type SettleObserver = Callable[[int], bool]
type SettleActs = Tensor | Iterable[Tensor]

T = TypeVar("T")


class SettleIterate[T]:
    """Mutable carrier for the value a settle loop advances.

    Loops rebind their iterate each step (a kernel step returns a new
    activation list, not an in-place update), so a closure-based driver
    needs a box rather than a captured name.
    """

    __slots__ = ("value",)

    def __init__(self, value: T) -> None:
        self.value = value


class FiniteGuard:
    """Lazily-synchronised NaN/Inf detector for a settle loop.

    A per-step guard written as ``if not torch.isfinite(a).all()`` reads a
    device tensor to the host once per activation per step. Each of those
    reads is a stream synchronisation: ~230 us on CUDA regardless of tensor
    size, and it drains the launch queue so the settle cannot overlap its own
    kernels. Nine dynamics paid it 25920 times over a 20-cell campaign — 4.3 s
    of an 8.0 s wall, for a check that is asking a question whose answer does
    not change until it is read.

    So the answer stays on device. Each step folds its activations into one
    running flag with pure tensor ops, and the host reads that flag once, when
    the loop ends. The earliest offending step is recorded on device too, so
    the raise still names the step that diverged rather than the last one.

    The guarantee is unchanged in the only sense that matters — a settle that
    goes non-finite raises ``RuntimeError`` instead of returning poisoned
    activations — and the cost drops from one sync per activation per step to
    one per loop.

    One guard per loop. Each ``observe`` names the quantity it is watching, so
    the raise can say which one diverged. Tensors are assumed to stay on one
    device for the loop's duration, as the settle loops themselves assume.
    """

    __slots__ = ("_device", "_first_bad")

    def __init__(self) -> None:
        self._device: torch.device | None = None
        self._first_bad: dict[str, torch.Tensor] = {}

    def observe(self, what: str, acts: SettleActs, step: int) -> None:
        """Fold one step's activations into the running flag. No host read."""
        import torch

        tensors = (acts,) if isinstance(acts, torch.Tensor) else tuple(acts)
        for tensor in tensors:
            if self._device is None:
                self._device = tensor.device
                self._first_bad = {
                    name: flag.to(tensor.device)
                    for name, flag in self._first_bad.items()
                }
            if (first_bad := self._first_bad.get(what)) is None:
                first_bad = torch.full((), -1, dtype=torch.long, device=tensor.device)
            diverged = torch.logical_not(torch.isfinite(tensor).all())
            marker = torch.full((), step, dtype=torch.long, device=tensor.device)
            self._first_bad[what] = torch.where(
                diverged, torch.minimum(first_bad, marker), first_bad
            )

    def raise_if_diverged(self) -> None:
        """The loop's one host read; raise if any observed step went non-finite."""
        for what, flag in self._first_bad.items():
            first = int(flag)
            if first >= 0:
                raise RuntimeError(f"NaN/Inf detected in {what} at step {first}")


def run_settle_loop(
    advance: SettleAdvance,
    *,
    max_steps: int,
    after_step: SettleObserver | None = None,
    guard: FiniteGuard | None = None,
) -> int:
    """Iterate ``advance`` up to ``max_steps`` times; return steps executed.

    Args:
        advance: Advances the iterate by one step, given the step index.
        max_steps: Horizon. The loop runs this many steps unless the
            observer stops it earlier — never fewer.
        after_step: Called after each executed step with its index; return
            ``True`` to stop. Never consulted to decide whether the *next*
            step runs before that step has been executed.
        guard: Accumulates each executed step's finiteness on device; the
            driver reads it once after the loop and raises if any step went
            non-finite. Omit to run unguarded.

    Returns:
        Number of steps actually executed.

    Raises:
        RuntimeError: If ``guard`` observed a non-finite step.
    """
    steps = 0
    try:
        for step in range(max_steps):
            advance(step)
            steps = step + 1
            if after_step is not None and after_step(step):
                break
    finally:
        if guard is not None:
            guard.raise_if_diverged()
    return steps


def checkpointed[T](advance: Callable[[int], T]) -> Callable[[int], T]:
    """Wrap ``advance`` so every call recomputes in backward."""

    def _checkpointed(step: int) -> T:
        from torch.utils import checkpoint

        return checkpoint.checkpoint(advance, step, use_reentrant=False)

    return _checkpointed


def checkpointed_every[T](
    advance: Callable[[int], T], every: int
) -> Callable[[int], T]:
    """Wrap ``advance`` so step *n* recomputes when ``n % every == 0``.

    Step 0 is never checkpointed: the first iteration builds the autograd
    graph, and there is nothing yet to recompute.
    """

    def _checkpointed_every(step: int) -> T:
        if step == 0 or step % every != 0:
            return advance(step)
        from torch.utils import checkpoint

        return checkpoint.checkpoint(advance, step, use_reentrant=False)

    return _checkpointed_every
