"""TODO92 §3.8: the tabular advantage on a ruler that can carry a claim.

Input (measured, §3.13): `local_goodness` beats `gradient` by **+0.0158**
val_acc on a single 114-row `breast_cancer` holdout (resolution 0.88 pp), so
the effect was about 1.8 held-out rows. This probe replaces the single holdout
with the task's own declared split — `TabularTask.fold_indices(5)`, stratified,
`random_state=0` — where every one of the 569 rows is held out exactly once.
Fold-mean resolution is 1/569 = **0.18 pp**, five times finer than the effect.

Instrument: ``train_on_task`` drives the same ``SystemTrainer`` the kernel
builds, with the same config (``max_epochs``, device, seed, no batch limits);
the system is composed by ``compose_cell_system`` at the §3.13 coordinate
(digital / feedforward / instantaneous / null / gradient-or-`local_goodness` /
adam, ``geometry.hidden_dim=256``). Only the credit, its declared channel
(``credit.readout_error=True``) and the seed differ between arms. L2/20. The
score is the last epoch's ``val_acc`` — the metric the corpus cell reports.

Decision: the pre-registered `ThresholdRegistration` (+0.005, alpha 0.05,
min 5 seeds) in
``configs/preregistrations/t92_local_goodness_tabular_folds.json``, committed
before seed 1.

Run: uv run python scripts/probes/t92_local_goodness_tabular_folds.py --pilot
     uv run python scripts/probes/t92_local_goodness_tabular_folds.py
     uv run python scripts/probes/t92_local_goodness_tabular_folds.py --report-only

Measured 2026-11-15 (5 folds x 5 seeds x 2 arms, L2/20, CPU, 49 s):
gradient **0.9778 ± 0.0027**, `local_goodness` **0.9782 ± 0.0020**; paired
**+0.0003**, 95% CI [−0.0025, +0.0025], p=0.96, dz=0.10 — **FAIL** against the
+0.005 threshold. The §3.13 +1.58 pp does not replicate on the 569-row ruler.

Two findings travel with the number. (a) The fold instrument's eval site
matters at this effect size: a post-training ``task.evaluate`` pass (the
``cross_validate`` path) scored gradient 0.9782 / `local_goodness` 0.9757 —
paired −0.0025, CI [−0.0042, −0.0011] — so the site moves the paired
difference by ~0.3 pp even though both passes FAIL the +0.005 threshold. It
also moves individual folds by up to 0.9 pp, so the probe scores the trainer's
last-epoch ``val_acc``, where the corpus cell scores. (b) The credit is live in
this harness — one epoch of each arm at the same seed moves the 74,242
parameters by max |Δ| 0.0255 — and per-fold accuracy is quantized at
1/114 = 0.88 pp, so the fold mean resolves 0.18 pp. At 0.978 the task is near
its ceiling: this coordinate has ~2.2 pp of headroom, so a ≥0.5 pp advantage
was still detectable (CI half-width 0.25 pp) but a *win* is unlikely here by
construction.
"""

from __future__ import annotations

import argparse
import json
import random
import statistics
import time
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np
import torch

from computronium.core.system_trainer.config import SystemTrainerConfig
from computronium.core.system_trainer.train_task import train_on_task
from computronium.domains.tabular import TabularTask
from computronium.experiment.kernel.compose import compose_cell_system
from computronium.experiment.schema.coordinate import Coordinate
from computronium.validation.preregistration import (
    ThresholdRegistration,
    paired_comparison,
)

__all__ = ["main"]

if TYPE_CHECKING:
    from collections.abc import Mapping

ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "experiments/t92_local_goodness_tabular_folds.json"
REGISTRATION = ROOT / "configs/preregistrations/t92_local_goodness_tabular_folds.json"
TASK = "breast_cancer"
SEEDS = (67, 68, 69, 70, 71)
PILOT_SEED = 42
N_FOLDS = 5
EPOCHS = 20
CONTROL = "gradient"
TREATMENT = "local_goodness"
CHANNEL: dict[str, object] = {"credit.readout_error": True}
PARAMS: dict[str, object] = {"geometry.hidden_dim": 256}


def _coordinate(credit: str) -> Coordinate:
    params = PARAMS | (CHANNEL if credit == TREATMENT else {})
    return Coordinate(
        substrate="digital",
        geometry="feedforward",
        dynamics="instantaneous",
        plasticity="null",
        credit=credit,
        update="adam",
        params=params,
    )


def _seed_all(seed: int) -> None:
    torch.manual_seed(seed)
    np.random.seed(seed)
    random.seed(seed)


def _factory(credit: str, task: TabularTask):
    def build(input_dim: int, output_dim: int):
        return compose_cell_system(
            coordinate=_coordinate(credit),
            geometry={"hidden_dim": 256},
            input_shape=(input_dim,),
            output_dim=output_dim,
            task=task,
        ).system

    return build


def _arm_folds(credit: str, seed: int, task: TabularTask) -> list[float]:
    """Fold-mean val_acc per seed, read where the kernel cell reads it.

    ``train_on_task`` drives the same ``SystemTrainer`` and config the kernel
    builds, and the last epoch's ``val_acc`` is the metric the corpus cell
    reports (``_update_task_metrics`` prefers the trainer history). A
    post-training ``task.evaluate`` pass is a different eval site and reads
    ~2 pp higher, so it cannot be compared with a corpus cell.
    """
    scores: list[float] = []
    for fold in range(N_FOLDS):
        task.set_fold(fold, N_FOLDS)
        _seed_all(seed)
        config = SystemTrainerConfig(
            max_epochs=EPOCHS, device=str(task.device), seed=seed, track_energy=False
        )
        history = train_on_task(_factory(credit, task), task, config)
        scores.append(float(history[-1]["val_acc"]))
    return scores


def _pilot(device: str) -> int:
    task = TabularTask(name=TASK, dataset_name=TASK, device=device)
    task.setup()
    for credit in (CONTROL, TREATMENT):
        task.set_fold(0, N_FOLDS)
        _seed_all(PILOT_SEED)
        started = time.perf_counter()
        config = SystemTrainerConfig(max_epochs=1, track_energy=False, device=device)
        trained: list[object] = []

        def factory(input_dim: int, output_dim: int):
            system = _factory(credit, task)(input_dim, output_dim)
            trained.append(system)
            return system

        train_on_task(factory, task, config)
        system = trained[-1]
        system.eval()  # type: ignore[attr-defined]
        metrics = task.evaluate(system)  # type: ignore[arg-type]
        print(
            f"pilot {credit:16} seed={PILOT_SEED} fold=0/5 epoch=1 "
            f"val_acc={metrics.accuracy:.4f} "
            f"({time.perf_counter() - started:.1f}s)",
            flush=True,
        )
    return 0


def _fold_means(results: Mapping[str, object]) -> dict[str, list[float]]:
    arms = results["arms"]
    if not isinstance(arms, dict):
        raise TypeError("results['arms'] must be a mapping")
    means: dict[str, list[float]] = {}
    for arm in (CONTROL, TREATMENT):
        data = arms[arm]
        if not isinstance(data, dict) or not isinstance(data["fold_means"], list):
            raise TypeError(f"arm {arm!r} is incomplete")
        means[arm] = [float(value) for value in data["fold_means"]]
    return means


def _report(results: Mapping[str, object]) -> int:
    registration = ThresholdRegistration.load(REGISTRATION)
    means = _fold_means(results)
    for arm, measured in means.items():
        print(
            f"{arm:16}: n={len(measured)} "
            f"mean={statistics.mean(measured):.4f} "
            f"sd={statistics.stdev(measured) if len(measured) > 1 else 0.0:.4f}"
        )
    if any(len(measured) < len(SEEDS) for measured in means.values()):
        print("incomplete")
        return 2
    result = paired_comparison(means[TREATMENT], means[CONTROL], seed=0)
    passed = result.passes(registration)
    print(
        f"paired {TREATMENT} - {CONTROL}: {result.mean_diff:+.4f} "
        f"95% CI [{result.ci_lower:+.4f}, {result.ci_upper:+.4f}] "
        f"p={result.p_value:.4f} dz={result.cohens_dz:.2f}"
    )
    print(
        f"verdict: {'PASS' if passed else 'FAIL'} "
        f"(threshold +{registration.threshold:.4f})"
    )
    return 0 if passed else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true")
    parser.add_argument("--report-only", action="store_true")
    parser.add_argument("--device", default="cpu")
    args = parser.parse_args(argv)

    if args.pilot:
        return _pilot(args.device)

    if args.report_only:
        with RESULTS.open(encoding="utf-8") as f:
            return _report(json.load(f))

    task = TabularTask(name=TASK, dataset_name=TASK, device=args.device)
    task.setup()
    results: dict[str, object] = {"task": TASK, "created": "2026-11-15", "arms": {}}
    arms: dict[str, dict[str, object]] = results["arms"]  # type: ignore[assignment]
    started = time.perf_counter()
    for credit in (CONTROL, TREATMENT):
        per_seed = {str(seed): _arm_folds(credit, seed, task) for seed in SEEDS}
        fold_means = [statistics.mean(per_seed[str(seed)]) for seed in SEEDS]
        arms[credit] = {
            "per_fold": per_seed,
            "fold_means": fold_means,
            "mean": statistics.mean(fold_means),
            "sd": statistics.stdev(fold_means),
        }
        print(
            f"{credit:16}: fold-mean {arms[credit]['mean']:.4f} "
            f"± {arms[credit]['sd']:.4f} over {len(SEEDS)} seeds",
            flush=True,
        )
    results["walltime_s"] = round(time.perf_counter() - started, 1)
    RESULTS.parent.mkdir(parents=True, exist_ok=True)
    with RESULTS.open("w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
        f.write("\n")
    print(f"results {RESULTS.relative_to(ROOT)}")
    return _report(results)


if __name__ == "__main__":
    raise SystemExit(main())
