"""Per-row re-measurement (TODO23 §12, difficulty-calibration follow-up).

Rows ff_mlp / fa_mlp / pepita_mlp carry ladder-era Pareto accuracy
(0.83 / 0.38 / 0.10) recorded on the OLD quick task (scale 2.0, noise
0.5). On the calibrated task (scale 1.2, noise 1.5) their campaigns will
honestly fail BenchmarkReproduction until each row gets its own measured
campaign. This probe runs the §11-compliant measurement (the campaign
construction path: cand.build(spec) + Lab.train with the guard) at
3 seeds x {10, 20} epochs and prints per-seed accuracies.

uv run python scripts/probes/remeasure_legacy_rows.py
Walltime printed, never recorded.
"""

from __future__ import annotations

import time

from computronium_lab.lab import Lab
from computronium_lab.synthesis.catalog import CATALOG
from computronium_lab.synthesis.spec import Constraints, ProblemSpec
from computronium_lab.training import TrainOptions

spec = ProblemSpec(
    task="classification",
    dataset="gaussian_blobs",
    constraints=Constraints(substrate="digital"),
    objectives=("accuracy",),
    input_dim=32,
    num_classes=4,
)

lab = Lab(device="cpu")

for name in ("ff_mlp", "fa_mlp", "pepita_mlp"):
    cand = next(c for c in CATALOG if c.name == name)
    for epochs in (10, 20):
        t0 = time.perf_counter()
        accs = []
        for seed in (0, 1, 2):
            lab.seed = seed
            system = cand.build(spec)
            result = lab.train(
                system,
                epochs=epochs,
                spec=spec,
                options=TrainOptions(stability_guard=True),
            )
            accs.append(float(result.metrics["accuracy"]))
        print(
            f"{name} @ {epochs}ep: "
            f"{[round(a, 3) for a in accs]} "
            f"mean={sum(accs) / len(accs):.3f} "
            f"({time.perf_counter() - t0:.1f}s)"
        )
