"""Registered derived operators (TODO26 T26.F.1, spec §9.4).

Every Derived row stores its inputs so :func:`compute_derived` can
recompute the value byte-identically from the ledger alone.
"""

from __future__ import annotations

import statistics
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Literal

from ceec.stats import chance_verdict

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping, Sequence

    from ceec import models
    from ceec.store import CEECStore

__all__ = ["OPERATORS", "Operator", "compute_derived"]


@dataclass(frozen=True, slots=True)
class Operator:
    """A named summary or relation over ledger inputs.

    ``fn`` receives ``{input_name: [float, ...]}`` resolved from the
    referenced evidence/derived rows and must be pure.
    """

    name: str
    kind: Literal["summary", "relation"]
    fn: Callable[..., Any]
    assumptions: tuple[str, ...] = ()


def _all_values(values: Mapping[str, Sequence[float]]) -> list[float]:
    return [v for seq in values.values() for v in seq]


def _mean(seq: Sequence[float]) -> float:
    return statistics.fmean(seq)


def _require_keys(values: Mapping[str, Sequence[float]], *keys: str) -> None:
    missing = [k for k in keys if k not in values]
    if missing:
        raise ValueError(f"operator requires inputs {keys}; missing {missing}")


def _mean_op(values: Mapping[str, Sequence[float]], _params: object = None) -> float:
    return _mean(_all_values(values))


def _median_op(values: Mapping[str, Sequence[float]], _params: object = None) -> float:
    return statistics.median(_all_values(values))


def _spread_op(values: Mapping[str, Sequence[float]], _params: object = None) -> float:
    vals = _all_values(values)
    return statistics.pstdev(vals) if len(vals) > 1 else 0.0


def _contrast_op(
    values: Mapping[str, Sequence[float]], _params: object = None
) -> float:
    _require_keys(values, "left", "right")
    return _mean(values["left"]) - _mean(values["right"])


def _slope_op(values: Mapping[str, Sequence[float]], _params: object = None) -> float:
    vals = _all_values(values)
    n = len(vals)
    if n < 2:
        raise ValueError("slope requires >= 2 ordered values")
    xs = range(n)
    mx, my = (n - 1) / 2, _mean(vals)
    denom = sum((x - mx) ** 2 for x in xs)
    return sum((x - mx) * (y - my) for x, y in zip(xs, vals, strict=True)) / denom


def _dominance_op(
    values: Mapping[str, Sequence[float]], _params: object = None
) -> float:
    _require_keys(values, "left", "right")
    pairs = list(zip(values["left"], values["right"], strict=True))
    if not pairs:
        raise ValueError("dominance requires non-empty paired inputs")
    return sum(a > b for a, b in pairs) / len(pairs)


def _replication_op(
    values: Mapping[str, Sequence[float]], _params: object = None
) -> bool:
    means = [_mean(seq) for seq in values.values() if seq]
    if len(means) < 2:
        raise ValueError("replication requires >= 2 input groups")
    return max(means) - min(means) <= 2.0 * statistics.pstdev(
        [v for seq in values.values() for v in seq] or [0.0]
    )


def _chance_band_op(
    values: Mapping[str, Sequence[float]], parameters: Mapping[str, Any] | None = None
) -> bool:
    params = parameters or {}
    verdict = chance_verdict(
        _all_values(values),
        int(params.get("n_eval", 1)),
        chance=float(params.get("chance", 0.5)),
    )
    return verdict.mean_at_chance


OPERATORS: Mapping[str, Operator] = {
    "mean": Operator("mean", "summary", _mean_op),
    "median": Operator("median", "summary", _median_op),
    "spread": Operator("spread", "summary", _spread_op),
    "contrast": Operator(
        "contrast", "relation", _contrast_op, ("left/right groups are comparable",)
    ),
    "slope": Operator(
        "slope", "summary", _slope_op, ("values are ordered observations",)
    ),
    "dominance": Operator(
        "dominance", "relation", _dominance_op, ("inputs are paired",)
    ),
    "replication": Operator(
        "replication",
        "relation",
        _replication_op,
        ("per-input means should agree within 2 sigma",),
    ),
    "chance_band": Operator(
        "chance_band",
        "summary",
        _chance_band_op,
        ("binomial standard error over the evaluation split",),
    ),
}


def _ref_values(store: CEECStore, ref: str) -> list[float]:
    prefix = ref.split("-", 1)[0]
    if prefix == "E":
        evidence = store.get_evidence(ref)
        out: list[float] = []
        for artifact_id in store.evidence_artifacts(evidence.id):
            payload = _artifact_payload(store, artifact_id)
            out.extend(_numeric_leaf_values(payload))
        return out
    if prefix == "D":
        value = store.get_derived(ref).value
        return (
            [float(value)]
            if isinstance(value, (int, float))
            else _numeric_leaf_values(value)
        )
    if prefix == "A":
        return _numeric_leaf_values(_artifact_payload(store, ref))
    raise ValueError(f"unsupported derived-input ref {ref!r}")


def _artifact_payload(store: CEECStore, artifact_id: str) -> Any:
    import json
    from pathlib import Path

    artifact = store.get_artifact(artifact_id)
    try:
        return json.loads(Path(artifact.uri).read_text(encoding="utf-8"))
    except OSError, ValueError:
        return []


def _numeric_leaf_values(node: Any) -> list[float]:
    if isinstance(node, bool):
        return []
    if isinstance(node, (int, float)):
        return [float(node)]
    if isinstance(node, dict):
        return [v for child in node.values() for v in _numeric_leaf_values(child)]
    if isinstance(node, (list, tuple)):
        return [v for child in node for v in _numeric_leaf_values(child)]
    return []


def compute_derived(
    store: CEECStore,
    operator: str,
    inputs: Mapping[str, Sequence[str]],
    *,
    scope: models.Scope,
    parameters: Mapping[str, Any] | None = None,
) -> models.Derived:
    """Resolve inputs from the ledger, apply the operator, record the row."""
    op = OPERATORS[operator]
    resolved: dict[str, list[float]] = {}
    for name, refs in inputs.items():
        values: list[float] = []
        for ref in refs:
            values.extend(_ref_values(store, ref))
        resolved[name] = values
    value: Any = op.fn(resolved, parameters)
    return store.record_derived(
        type_=op.kind,
        operator=operator,
        inputs={k: list(v) for k, v in inputs.items()},
        scope=scope,
        value=value,
        parameters=dict(parameters or {}),
        assumptions=list(op.assumptions),
        provenance={"recomputable": True, "operator": operator},
    )
