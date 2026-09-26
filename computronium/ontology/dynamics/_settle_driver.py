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

from collections.abc import Callable
from typing import TypeVar

type SettleAdvance = Callable[[int], None]
type SettleObserver = Callable[[int], bool]

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


def run_settle_loop(
    advance: SettleAdvance,
    *,
    max_steps: int,
    after_step: SettleObserver | None = None,
) -> int:
    """Iterate ``advance`` up to ``max_steps`` times; return steps executed.

    Args:
        advance: Advances the iterate by one step, given the step index.
        max_steps: Horizon. The loop runs this many steps unless the
            observer stops it earlier — never fewer.
        after_step: Called after each executed step with its index; return
            ``True`` to stop. Never consulted to decide whether the *next*
            step runs before that step has been executed.

    Returns:
        Number of steps actually executed.
    """
    steps = 0
    for step in range(max_steps):
        advance(step)
        steps = step + 1
        if after_step is not None and after_step(step):
            break
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
