"""P0.1 ruler calibration: BP-reachable accuracy per task at standard budget.

TODO27.md §Phase 0: no accuracy verdict on a task whose backprop ceiling at
the same budget is unknown. This probe sweeps the offline task catalog with
the native backprop MLP (quick-mode batch caps), records per-task
BP-reachable validation accuracy plus the chance band, and writes the ruler
table JSON. Only BP-beats-chance tasks are campaign-eligible (G1).

Output: artifacts/ruler_table.json (keyed by task; a task with
``eligible: false`` is fenced out of the grid).

Run: uv run python scripts/probes/ruler_calibration.py [--tasks mnist,iris ...]
Walltime note: full catalog sweep is a background job; the default task set
here is the fast offline subset used to validate the instrument.
"""

import argparse
import json
import math
import time
from pathlib import Path

from computronium.core.system_trainer import SystemTrainer, SystemTrainerConfig
from computronium.core.utils.device import get_device
from computronium.domains.factory import create_task
from computronium.experiment.param_estimator import resolve_native_model

__all__ = ["calibrate_task", "main"]

BUDGET_EPOCHS = 3
BUDGET_BATCH = 64
HIDDEN = 64
#: P0.3: the budget's lr is a micro-sweep, not a carried-over constant.
LR_SWEEP = (1e-3, 1e-2)


def calibrate_task(task_name: str, epochs: int = BUDGET_EPOCHS) -> dict[str, object]:
    """Measure the BP ceiling and chance band for one task.

    The lr is micro-swept (P0.3) and the best run is the ruler row —
    the ceiling must not be an artifact of one arbitrary lr.
    ``epochs`` matches a cell budget for the control arm (rev 10).
    """
    task = create_task(task_name, device=str(get_device()), quick_mode=True)
    task.setup()
    input_dim = task.input_dim
    if isinstance(input_dim, tuple | list):
        input_dim = int(math.prod(input_dim))
    output_dim = int(task.output_dim or 1)
    chance = 1.0 / output_dim

    best: dict[str, object] | None = None
    best_acc = -1.0
    for lr in LR_SWEEP:
        system = resolve_native_model("backprop_mlp")(
            input_dim, HIDDEN, output_dim, lr=lr, device=str(get_device())
        )
        t0 = time.time()
        with SystemTrainer(
            system,  # type: ignore[arg-type]
            SystemTrainerConfig(max_epochs=epochs, batch_size=BUDGET_BATCH),
            task.get_dataloader("train"),  # type: ignore[attr-defined]
            task.get_dataloader("val"),  # type: ignore[attr-defined]
        ) as trainer:
            history = trainer.fit()
        last = history[-1] if history else {}
        val_acc = float(last.get("val_acc", 0.0) or 0.0)
        if val_acc > best_acc:
            best_acc = val_acc
            best = {
                "bp_val_accuracy": val_acc,
                "lr": lr,
                "walltime_s": round(time.time() - t0, 1),
            }
    assert best is not None  # ruff: ignore[assert] — loop runs at least once
    val_acc = best_acc
    return {
        "task": task_name,
        "bp_val_accuracy": val_acc,
        "chance_band": chance,
        "beats_chance": val_acc > chance + 0.05,
        "eligible": val_acc > chance + 0.05,
        "epochs": epochs,
        "batch_size": BUDGET_BATCH,
        "hidden_dim": HIDDEN,
        "lr": best["lr"],
        "walltime_s": best["walltime_s"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--tasks",
        default="digits,iris,wine,breast_cancer,circles,spiral",
        help="Comma-separated task names (offline-resolvable subset by default)",
    )
    parser.add_argument(
        "--out", default="artifacts/ruler_table.json", help="Output ruler table path"
    )
    parser.add_argument(
        "--epochs",
        default="3",
        help="Comma-separated epoch budgets (e.g. '1,5' for the rev-10 "
        "matched-budget control arm; 3 = the standard ruler)",
    )
    args = parser.parse_args()

    rows = []
    for epochs_str in args.epochs.split(","):
        epochs = int(epochs_str.strip())
        for name in args.tasks.split(","):
            name = name.strip()
            try:
                row = calibrate_task(name, epochs=epochs)
            except Exception as exc:  # ruff: ignore[blind-except] — one bad task must not kill the sweep
                row = {"task": name, "error": str(exc), "eligible": False}
            rows.append(row)
            print(json.dumps(row))

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"rows": rows}, indent=2), encoding="utf-8")
    print(f"ruler table -> {out}")


if __name__ == "__main__":
    main()
