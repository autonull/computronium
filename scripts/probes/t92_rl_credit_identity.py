"""TODO92 §3.3b: is the RL credit axis inert, or merely untuned?

RLSystemTrainer optimises ``system.geometry.params`` with DDPG and never calls
the composed credit, so the rule is that two credits produce the same episode
returns. This probe measures that prediction on one cell: the pendulum L0
coordinate from ``experiments/t92_rl_400ep.duckdb`` with ``gradient`` and
``homeostatic``, one epoch, seed 42.

Measured (2026-11-14, RTX 3080): both credits return mean_reward
-1536.6081020017289 in 15 s, bit-identical to the recorded gradient positive
control. The refusal row ``rl_credit_must_be_error_blind`` encodes this rule.

Run: uv run python scripts/probes/t92_rl_credit_identity.py
Walltime printed, never recorded.
"""

from __future__ import annotations

import time

from computronium.experiment.kernel.evaluate import evaluate_cell
from computronium.experiment.schema.coordinate import Coordinate, Schedule

__all__ = ["main"]

CREDITS = ("gradient", "homeostatic")


def _coordinate(credit: str) -> Coordinate:
    return Coordinate(
        substrate="digital",
        geometry="feedforward",
        dynamics="instantaneous",
        plasticity="null",
        credit=credit,
        update="euclidean",
        params={},
    )


def _schedule() -> Schedule:
    return Schedule(
        fidelity="L0",
        seed=42,
        n_seeds=1,
        epochs=1,
        batch_limit=0,
        budget_id="L0_initial",
        task_id="pendulum",
        param_budget=0,
        device="cuda",
    )


def main() -> int:
    values: dict[str, float] = {}
    for credit in CREDITS:
        started = time.perf_counter()
        result = evaluate_cell(_coordinate(credit), _schedule())
        values[credit] = float(result.metrics["mean_reward"])
        print(
            f"{credit:14} mean_reward={values[credit]:.6f} "
            f"({time.perf_counter() - started:.1f}s)"
        )
    identical = len(set(values.values())) == 1
    print(f"identical={identical} values={values}")
    return 0 if identical else 1


if __name__ == "__main__":
    raise SystemExit(main())
