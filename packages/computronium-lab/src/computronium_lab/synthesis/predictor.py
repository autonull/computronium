"""I(C,U,P) viability model v2 (TODO23 T23.1.2).

Depth-matched, ψ-conditional, geometry-aware viability predictor over the
measured I(C,U) ladder corpus (`data/icu_measurements.csv`). Interpretable by
design (decision tree + calibrated logistic) — TODO23 §8 anti-black-box rule.

The fit is **depth-matched** (TODO17 §5.1): the d32 campaign rows are a
sampling boundary — including them degrades global fit (CV 0.892→0.849,
held-out geometry 0.944→0.722, `logs/w17_icu_fit.log`), so `fit` excludes
depths above `depth_max` by default.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.preprocessing import OneHotEncoder
from sklearn.tree import DecisionTreeClassifier

VIABILITY_THRESHOLD = 0.75
CREDIT_CLASS: dict[str, str] = {
    "bp": "exact_gradient",
    "bptt": "exact_gradient",
    "eqprop": "energy_contrast",
    "fa": "projected_pseudo",
    "pepita": "projected_pseudo",
    "local_contrastive": "goodness_contrast",
    "ff": "goodness_contrast",
}
UPDATE_CLASS: dict[str, str] = {
    "euclid": "euclidean",
    "euclid.2": "euclidean",
    "adam": "per_coordinate",
    "muon": "orthogonalizing",
    "muon.02": "orthogonalizing",
    "ortho_adam": "orthogonalizing",
    "ortho": "orthogonalizing",
    "lion": "sign_based",
}
GEOMETRY_CLASS: dict[str, str] = {
    "mlp": "stack",
    "lattice": "stack",
    "nca": "iterative",
    "ntm": "memory",
    "recurrent": "stack",
}
DEFAULT_DEPTH_MAX = 2


@dataclass(frozen=True, slots=True)
class MechanismFeatures:
    """I(C,U,P) features for one candidate mechanism coordinate."""

    credit_class: str
    update_class: str
    geometry: str
    geometry_class: str
    task: str
    mechanism_class: str
    plasticity: str
    depth: int
    width: int
    interaction_i: float

    def as_row(self) -> tuple[list[str], list[float]]:
        cat = [
            self.credit_class,
            self.update_class,
            self.geometry,
            self.geometry_class,
            self.task,
            self.mechanism_class,
            self.plasticity,
        ]
        return cat, [float(self.depth), float(self.width), self.interaction_i]


class ViabilityModel:
    """Depth-matched viability classifier with geometry-holdout diagnostics."""

    def __init__(self, corpus: Path | None = None) -> None:
        self._corpus = corpus
        self._tree: DecisionTreeClassifier | None = None
        self._logistic: LogisticRegression | None = None
        self._encoder: OneHotEncoder | None = None
        self.cv_accuracy: float = 0.0
        self.holdout_geometry_accuracy: float = 0.0

    def fit(self, depth_max: int = DEFAULT_DEPTH_MAX) -> ViabilityModel:
        rows = [
            r
            for r in _load_rows(self._resolve_corpus())
            if int(r["depth"]) <= depth_max
        ]
        cat, num, y = _featurize(rows)
        x, enc = _encode(cat, num)
        self._encoder = enc
        cv = StratifiedKFold(5, shuffle=True, random_state=0)
        scores = cross_val_score(
            LogisticRegression(max_iter=2000, random_state=0), x, y, cv=cv
        )
        self.cv_accuracy = float(scores.mean())
        self._tree = DecisionTreeClassifier(
            max_depth=4, min_samples_leaf=5, random_state=0
        ).fit(x, y)
        self._logistic = LogisticRegression(max_iter=2000, random_state=0).fit(x, y)
        self._holdout_geometry(cat, num, y)
        return self

    def predict(self, features: MechanismFeatures) -> float:
        """P(viable) for one candidate coordinate."""
        proba = self._proba(features)
        return float(proba[1])

    def rationale(self, features: MechanismFeatures) -> str:
        """Human-readable tree path — the provenance trace for a coordinate."""
        tree, encoder = self._tree, self._encoder
        if tree is None or encoder is None:
            raise RuntimeError("ViabilityModel not fitted; call fit() first")
        cat, num = features.as_row()
        x = np.hstack([
            np.asarray(encoder.transform([cat]), dtype=np.float64),
            np.asarray([num], dtype=np.float64),
        ])[0]
        names = np.concatenate([
            encoder.get_feature_names_out(),
            np.array(["depth", "width", "interaction_i"]),
        ])
        return _tree_path(tree.tree_, names, x)  # type: ignore[arg-type]

    def _proba(self, features: MechanismFeatures) -> np.ndarray:
        logistic, encoder = self._logistic, self._encoder
        if logistic is None or encoder is None:
            raise RuntimeError("ViabilityModel not fitted; call fit() first")
        cat, num = features.as_row()
        x = np.hstack([
            np.asarray(encoder.transform([cat]), dtype=np.float64),
            np.asarray([num], dtype=np.float64),
        ])
        return logistic.predict_proba(x)[0]

    def _holdout_geometry(
        self, cat: list[list[str]], num: list[list[float]], y: np.ndarray
    ) -> None:
        """§4.3 diagnostic: hold out the recorded lattice regime (the pinned
        0.944 claim, TODO16 Phase 4.3); fall back to the largest geometry."""
        groups: dict[str, list[int]] = {}
        for i, row in enumerate(cat):
            groups.setdefault(row[2], []).append(i)
        holdout_name = (
            "lattice"
            if "lattice" in groups
            else max(groups, key=lambda g: len(groups[g]))
        )
        holdout_idx = groups[holdout_name]
        if len(groups) < 2 or not holdout_idx:
            self.holdout_geometry_accuracy = 0.0
            return
        train_idx = [i for i in range(len(cat)) if i not in set(holdout_idx)]
        enc = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
        x_tr = np.hstack([
            np.asarray(
                enc.fit_transform([cat[i] for i in train_idx]), dtype=np.float64
            ),
            np.asarray([num[i] for i in train_idx], dtype=np.float64),
        ])
        x_te = np.hstack([
            np.asarray(enc.transform([cat[i] for i in holdout_idx]), dtype=np.float64),
            np.asarray([num[i] for i in holdout_idx], dtype=np.float64),
        ])
        model = LogisticRegression(max_iter=2000, random_state=0).fit(
            x_tr, y[train_idx]
        )
        self.holdout_geometry_accuracy = float(
            (model.predict(x_te) == y[holdout_idx]).mean()
        )

    def _resolve_corpus(self) -> Path:
        if self._corpus is not None:
            return self._corpus
        here = Path(__file__).resolve()
        for parent in here.parents:
            candidate = parent / "data" / "icu_measurements.csv"
            if candidate.exists():
                return candidate
        raise FileNotFoundError(
            "icu_measurements.csv not found; pass corpus= explicitly"
        )


def _load_rows(corpus: Path) -> list[dict[str, str]]:
    with corpus.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _featurize(
    rows: list[dict[str, str]],
) -> tuple[list[list[str]], list[list[float]], np.ndarray]:
    cat, num, y = [], [], []
    for r in rows:
        f = MechanismFeatures(
            credit_class=CREDIT_CLASS.get(r["credit"], "other"),
            update_class=UPDATE_CLASS.get(r["update"], "other"),
            geometry=r["geometry"],
            geometry_class=GEOMETRY_CLASS.get(r["geometry"], "other"),
            task=r["task"],
            mechanism_class=r["mechanism_class"],
            plasticity=r["plasticity"],
            depth=int(r["depth"]),
            width=int(r["width"]),
            interaction_i=float(r["interaction_i"]),
        )
        c, n = f.as_row()
        cat.append(c)
        num.append(n)
        y.append(int(float(r["accuracy"]) >= VIABILITY_THRESHOLD))
    return cat, num, np.array(y)


def _encode(
    cat: list[list[str]], num: list[list[float]]
) -> tuple[np.ndarray, OneHotEncoder]:
    enc = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
    x = np.hstack([
        np.asarray(enc.fit_transform(cat), dtype=np.float64),
        np.asarray(num, dtype=np.float64),
    ])
    return x, enc


class TreeStructure(Protocol):
    """Structural view of a fitted sklearn decision tree (``tree_``)."""

    children_left: np.ndarray
    children_right: np.ndarray
    feature: np.ndarray
    threshold: np.ndarray
    value: np.ndarray


def _tree_path(tree: TreeStructure, names: np.ndarray, x: np.ndarray) -> str:
    """Walk a fitted sklearn decision tree to its leaf."""
    node = 0
    steps: list[str] = []
    while int(tree.children_left[node]) != -1:
        idx = int(tree.feature[node])
        thr = float(tree.threshold[node])
        go_left = bool(x[idx] <= thr)
        steps.append(f"{names[idx]} {'<=' if go_left else '>'} {thr:.2f}")
        node = (
            int(tree.children_left[node]) if go_left else int(tree.children_right[node])
        )
    viable = bool(np.argmax(tree.value[node][0]) == 1)
    steps.append(f"→ viable={viable}")
    return "; ".join(steps)


__all__ = [
    "CREDIT_CLASS",
    "DEFAULT_DEPTH_MAX",
    "GEOMETRY_CLASS",
    "UPDATE_CLASS",
    "VIABILITY_THRESHOLD",
    "MechanismFeatures",
    "ViabilityModel",
]
