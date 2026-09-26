"""``python -m computronium.cli.export_trained_kernel`` — export a kernel backend.

**This entry point is disabled, and it says so at its own boundary rather than
raising an ``ImportError`` from a name.** It used to train through
``CoreTrainer(use_kernel=True)`` and export the *bound* backend — the whole
point of the command is that the exported weights are the ones a kernel
actually trained. ``CoreTrainer`` was removed in Sprint 7.6.10, and the
replacement cannot supply the missing half:

* A composed ``System`` trains through
  :func:`computronium.core.pipeline.run_train_step`, which has **no kernel
  arm**. ``dispatch_train_step`` reaches a backend by reading
  ``model._kernel_backend`` off an ``nn.Module``; a ``System`` has no such
  attribute and no equivalent.
* :meth:`KernelBackend.set_model_ref` is a per-family contract -- a
  ``list[nn.Linear]`` for FF and SNN, ``(layers, activation)`` for PC, a tile
  algorithm for TILE -- so "attach the system's geometry" is not one call.

Without both, an export serialises weights no kernel ran: an artifact that
looks trained and is not, which is worse than not exporting. The blocker and
its two contracts are recorded in ``TODO35.md``; what is left here is the
refusal, so a caller learns the boundary from the command instead of from a
traceback.
"""

from __future__ import annotations

import sys

from computronium.core.logging import get_logger

logger = get_logger()

BLOCKED = (
    "export_trained_kernel needs a kernel-backed System, and there is not one: "
    "a System trains through core.pipeline.run_train_step, which has no kernel "
    "arm, so the exported weights would not be the ones a kernel trained. "
    "TODO35.md records the two contracts that have to exist first -- a kernel "
    "arm on the System pipeline, and a per-family way to bind a System's "
    "geometry to a KernelBackend."
)

__all__ = ["BLOCKED", "main"]


def main(argv: list[str] | None = None) -> int:
    """Refuse, and name the missing capability. Always returns 1.

    Args:
        argv: Accepted so the console-script entry point has the usual shape.
            ``--explain`` prints the reason on stdout instead of the log.
    """
    args = list(sys.argv[1:] if argv is None else argv)
    if "--explain" in args:
        print(BLOCKED)
    else:
        logger.error(BLOCKED)
    return 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
