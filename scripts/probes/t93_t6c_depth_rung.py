"""T6c screen: does a stream-normalized stack train at the claim depth?

The pilot's plain stack is pinned at the L=32 plateau (val_acc 0.100, loss
2.2132 from step 200 to 1000). This probe measures the depth rung at the
claim point: L=8 vs L=32, plain vs ``stream_norm``, the normalized stack on
its own LR ladder because the plain ladder's 0.1/0.3/1.0 edge diverges under
unit-scale streams (measured 2026-11-16).

Regime: CIFAR-10 10k subset / full 10k test, W=1024, B=8192, 200 steps,
``backprop`` + ``EuclideanUpdate``, one seed. It informs TODO93 T6c's rung;
it is not a claim cell.

Measured 2026-11-16 (seed 11): plain L=8/L=32 = 0.419/0.100 (1061/4229 MB);
stream-normalized L=8 = 0.411/0.411/0.406 at LR 3e-3/1e-2/3e-2 (1602 MB) and
L=32 = 0.315/0.336/0.341 (6281 MB of the 6554 MB budget). The normalized pass
leaves the plateau at 1.45x the plain activation bytes and misses the L=8 floor
(0.409) by 6.8 pp; the rung's own box (`--rung`) is the cheaper confirmation
and carries the same verdict.
"""

from __future__ import annotations

import logging
import sys

from computronium.validation import memory_frontier as frontier

LRS = (3e-3, 1e-2, 3e-2)


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    x_train, y_train, x_test, y_test = frontier._cifar()
    point = frontier.PilotPoint()
    if not point.affordable():
        print(f"point unaffordable: {point.peak_mb():.0f} MB")
        return 1
    for depth in (8, 32):
        plain = frontier._measure(
            "backprop",
            point.scaled(depth=depth),
            lr=frontier.FROZEN_LR["backprop"],
            seed=frontier.PILOT_SEEDS[0],
            device="cuda",
            x_train=x_train,
            y_train=y_train,
            x_test=x_test,
            y_test=y_test,
        )
        print(
            f"L={depth} plain lr={frontier.FROZEN_LR['backprop']} "
            f"val={plain.val_acc:.3f} act={plain.activations_mb:.0f} MB",
            flush=True,
        )
        for lr in LRS:
            cell = frontier._measure(
                "backprop",
                point.scaled(depth=depth, stream_norm=True),
                lr=lr,
                seed=frontier.PILOT_SEEDS[0],
                device="cuda",
                x_train=x_train,
                y_train=y_train,
                x_test=x_test,
                y_test=y_test,
            )
            print(
                f"L={depth} stream_norm lr={lr:g} val={cell.val_acc:.3f} "
                f"act={cell.activations_mb:.0f} MB peak={cell.peak_mb:.0f} MB",
                flush=True,
            )
    return 0


if __name__ == "__main__":
    sys.exit(main())
