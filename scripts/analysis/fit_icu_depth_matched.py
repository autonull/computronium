"""Depth-matched I(C,U) held-out refit (TODO17 session-6 follow-up).

Session 6 recorded: adding the 72 campaign-7.1 rows (depth 32, d32
MNIST) degrades the held-out lattice fit 0.944 -> 0.722, diagnosed as a
*sampling* boundary (the lattice rows are ALL depth 2; the training mix
became depth-mismatched). This probe tests that diagnosis directly:
refit the held-out-geometry model with depth-matched training rows.

Arms:
  all-depths   — the session-6 fit (reproduces 0.722)
  shallow-only — train rows restricted to depth <= 2 (matches the
                 lattice rows' depth distribution)

Prediction: shallow-only recovers ~0.94 (the degradation is a depth-
sampling artifact, not a ψ/row-content effect). Falsification:
shallow-only stays ~0.72 (the campaign rows carry a content effect).

uv run python scripts/analysis/fit_icu_depth_matched.py
Walltime printed, never recorded.

RESULT (2026-09-10, 0.2 s): all-depths 0.722 (reproduces session 6);
shallow-only 0.944 — EXACT recovery of the anchor. The session-6
degradation is a depth-sampling artifact, confirmed: the I(C,U)
generalization law stands at matched training/eval depth; the d32
campaign rows are valid data but must be depth-matched (or the fit
depth-stratified) for held-out geometry claims.
"""

from __future__ import annotations

import csv
import time

from fit_icu_model import CSV, _featurize
from sklearn.linear_model import LogisticRegression


def _refit(rows: list, label: str) -> float:
    lat = [r for r in rows if r["geometry"] == "lattice"]
    train = [r for r in rows if r["geometry"] != "lattice"]
    x_tr, y_tr, _, enc = _featurize(train)
    x_te, y_te, _, _ = _featurize(lat, enc=enc)
    model = LogisticRegression(max_iter=2000, random_state=0).fit(x_tr, y_tr)
    acc = (model.predict(x_te) == y_te).mean()
    print(f"{label:>14}: train n={len(train)}, held-out lattice acc {acc:.3f}")
    return acc


def main() -> int:
    t0 = time.time()
    rows = list(csv.DictReader(CSV.open()))
    acc_all = _refit(rows, "all-depths")
    shallow = [r for r in rows if r["geometry"] == "lattice" or int(r["depth"]) <= 2]
    acc_shallow = _refit(shallow, "shallow-only")
    recovered = abs(acc_shallow - 0.944) <= 0.05
    print(
        f"\nVERDICT: depth-matched fit {'RECOVERS the 0.944 anchor' if recovered else 'does NOT recover (content effect)'} "
        f"(all {acc_all:.3f} vs shallow {acc_shallow:.3f}, anchor 0.944)"
    )
    print(f"walltime {time.time() - t0:.1f}s (printed, never recorded)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
