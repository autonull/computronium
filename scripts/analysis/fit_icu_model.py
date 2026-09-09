"""Flagship C (TODO16 §4.2): predict cell viability from I(C,U,P) features.

Decision tree (interpretable) + logistic regression (calibrated) on
data/icu_measurements.csv. Target: viable (accuracy ≥ 0.75) vs not.
5-fold stratified CV; held-out geometry validation (§4.3).

uv run python scripts/analysis/fit_icu_model.py
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.preprocessing import OneHotEncoder
from sklearn.tree import DecisionTreeClassifier

ROOT = Path(__file__).resolve().parents[2]
CSV = ROOT / "data" / "icu_measurements.csv"
VIABLE = 0.75

CREDIT_CLASS = {
    "bp": "exact_gradient",
    "bptt": "exact_gradient",
    "eqprop": "exact_gradient",
    "fa": "projected_pseudo",
    "pepita": "projected_pseudo",
    "local_contrastive": "goodness_contrast",
    "ff": "goodness_contrast",
}
UPDATE_CLASS = {
    "euclid": "euclidean",
    "euclid.2": "euclidean",
    "adam": "per_coordinate",
    "muon": "orthogonalizing",
    "muon.02": "orthogonalizing",
    "ortho_adam": "orthogonalizing",
    "ortho": "orthogonalizing",
    "lion": "sign_based",
}
GEOMETRY_CLASS = {
    "mlp": "stack",
    "lattice": "stack",
    "nca": "iterative",
    "ntm": "memory",
}


def load() -> tuple[np.ndarray, np.ndarray, list[str]]:
    rows = list(csv.DictReader(CSV.open()))
    x, y, names, _ = _featurize(rows)
    return x, y, names


def main() -> int:
    x, y, names = load()
    print(f"rows {len(y)}  viable {y.sum()} ({y.mean():.1%})  features {x.shape[1]}")

    dt = DecisionTreeClassifier(max_depth=4, min_samples_leaf=5, random_state=0)
    lr = LogisticRegression(max_iter=2000, random_state=0)
    cv = StratifiedKFold(5, shuffle=True, random_state=0)
    for name, model in (("tree", dt), ("logistic", lr)):
        scores = cross_val_score(model, x, y, cv=cv, scoring="accuracy")
        print(f"{name:>8} CV acc: {scores.mean():.3f} ± {scores.std():.3f}")

    dt.fit(x, y)
    imp = sorted(zip(dt.feature_importances_, names), reverse=True)[:8]
    print("\ntop tree features:")
    for v, n in imp:
        if v > 0:
            print(f"  {n}: {v:.3f}")

    heldout_geometry()
    return 0


def heldout_geometry() -> None:
    """§4.3: train on {mlp, nca, ntm}, predict lattice viability."""
    rows = list(csv.DictReader(CSV.open()))
    lat = [r for r in rows if r["geometry"] == "lattice"]
    rest = [r for r in rows if r["geometry"] != "lattice"]
    if not lat:
        print("\nheld-out geometry: no lattice rows")
        return
    x_tr, y_tr, _, enc = _featurize(rest)
    x_te, y_te, _, _ = _featurize(lat, enc=enc)
    model = LogisticRegression(max_iter=2000, random_state=0).fit(x_tr, y_tr)
    pred = model.predict(x_te)
    acc = (pred == y_te).mean()
    print(f"\nheld-out geometry (lattice, {len(y_te)} rows): acc {acc:.3f}")
    for r, p, y in zip(lat, model.predict_proba(x_te)[:, 1], y_te, strict=True):
        print(
            f"  {r['credit']} x {r['update']}: pred_viable_p={p:.2f} "
            f"actual={float(r['accuracy']):.3f} ({'viable' if y else 'not'})"
        )


def _featurize(
    rows: list[csv.DictReader], enc: OneHotEncoder | None = None
) -> tuple[np.ndarray, np.ndarray, list[str], OneHotEncoder]:
    cat, num, target = [], [], []
    for r in rows:
        acc = float(r["accuracy"])
        cat.append([
            CREDIT_CLASS.get(r["credit"], "other"),
            UPDATE_CLASS.get(r["update"], "other"),
            r["geometry"],
            GEOMETRY_CLASS.get(r["geometry"], "other"),
            r["task"],
            r["mechanism_class"],
        ])
        num.append([int(r["depth"]), int(r["width"]), float(r["interaction_i"])])
        target.append(int(acc >= VIABLE))
    if enc is None:
        enc = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
        cat_x = enc.fit_transform(cat)
    else:
        cat_x = enc.transform(cat)
    x = np.hstack([cat_x, np.array(num)])
    return (
        x,
        np.array(target),
        [*enc.get_feature_names_out(), "depth", "width", "interaction_i"],
        enc,
    )


if __name__ == "__main__":
    sys.exit(main())
