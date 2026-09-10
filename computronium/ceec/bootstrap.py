"""Bootstrap of the initial CEEC epistemic state (Phase F).

Instrument beliefs, hypothesis beliefs, goals, and pre-registered experiments
are loaded from `configs/ceec/`. Each bootstrap belief receives a provenance
evidence record referencing its configuration artifact, so no belief lacks
scope or evidence references.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from omegaconf import OmegaConf

from computronium.ceec import models
from computronium.ceec.store import CEECStore, StoreError

PROVENANCE_KIND = "event"


def _load(path: Path) -> dict[str, Any]:
    return OmegaConf.to_container(OmegaConf.load(path), resolve=True)  # type: ignore[return-value]


def _provenance_evidence(
    store: CEECStore, config_path: Path, kind: str, subject: str
) -> models.Evidence:
    artifact = store.ingest_artifact(
        config_path.read_bytes(),
        "bootstrap_config",
        {"config": str(config_path), "subject": subject},
    )
    return store.record_evidence(
        kind=PROVENANCE_KIND,
        scope=models.Scope(domain="bootstrap", extra={"config": str(config_path)}),
        artifact_refs=[artifact.id],
        axes=["bootstrap"],
        values_ref=artifact.uri,
        quality={"verification_level": 5, "bootstrap": True},
        notes=f"bootstrap provenance for {kind} {subject}",
    )


def bootstrap_instruments(store: CEECStore, config_dir: Path) -> list[str]:
    config_path = config_dir / "instruments.yaml"
    entries = _load(config_path).get("instruments", [])
    ids = []
    for entry in entries:
        ev = _provenance_evidence(store, config_path, "instrument", entry["id"])
        store.create_belief(
            statement=entry["statement"],
            type_="instrument",
            scope=_scope(entry.get("scope", {})),
            id_=entry["id"],
            evidence_refs=[ev.id],
        )
        ids.append(entry["id"])
    return ids


def bootstrap_beliefs(store: CEECStore, config_dir: Path) -> list[str]:
    config_path = config_dir / "beliefs.yaml"
    entries = _load(config_path).get("beliefs", [])
    ids = []
    for entry in entries:
        ev = _provenance_evidence(store, config_path, "belief", entry["id"])
        store.create_belief(
            statement=entry["statement"],
            type_=entry.get("type", "mechanism"),
            scope=_scope(entry.get("scope", {})),
            id_=entry["id"],
            evidence_refs=[ev.id],
        )
        probability = models.Probability(
            low=entry["probability"]["low"],
            high=entry["probability"]["high"],
            method="bootstrap_prior",
        )
        store.update_belief(
            entry["id"],
            probability,
            entry.get("uncertainty", "high"),
            entry.get("evidence_weight", "low"),
            entry.get("generality", "narrow"),
            "open",
            f"bootstrap prior from {config_path.name}",
        )
        ids.append(entry["id"])
    return ids


def bootstrap_goals(store: CEECStore, config_dir: Path) -> list[str]:
    config_path = config_dir / "goals.yaml"
    entries = _load(config_path).get("goals", [])
    ids = []
    for entry in entries:
        store.create_goal(
            statement=entry["statement"],
            kind=entry.get("kind", "science"),
            id_=entry["id"],
            belief_refs=entry.get("belief_refs", []),
        )
        utility = entry.get(
            "utility",
            {
                "science": 0.0,
                "program": 0.0,
                "resource": 0.0,
                "optionality": 0.0,
                "urgency": 0.0,
            },
        )
        store.revise_goal(
            entry["id"],
            utility,
            scalar_utility=entry.get("scalar_utility"),
            rationale=f"bootstrap utility from {config_path.name}",
        )
        ids.append(entry["id"])
    return ids


def experiment_from_config(config_path: Path | str) -> models.Experiment:
    """Build an ``Experiment`` model from its YAML config file."""
    entry = _load(Path(config_path)).get("experiment")
    if entry is None:
        raise StoreError(f"{config_path}: no 'experiment' section")
    pp = entry.get("prediction_probability")
    cost = entry.get("cost_estimate", {})
    return models.Experiment(
        id=entry["id"],
        question=entry["question"],
        rationale=entry["rationale"],
        scope=_scope(entry.get("scope", {})),
        target_beliefs=list(entry.get("target_beliefs", [])),
        target_goals=list(entry.get("target_goals", [])),
        design=dict(entry.get("design", {})),
        prediction=entry["prediction"],
        prediction_probability=(
            models.Probability(low=pp["low"], high=pp["high"], method=pp.get("method"))
            if pp
            else None
        ),
        controls=list(entry.get("controls", [])),
        metrics=list(entry.get("metrics", [])),
        budget=entry.get("budget", "quick"),
        cost_low=cost.get("low"),
        cost_high=cost.get("high"),
        falsification_criterion=entry["falsification_criterion"],
        overturn_criterion=entry["overturn_criterion"],
        hard_gates=list(entry.get("hard_gates", [])),
        created_at=entry.get("created_at", _now()),
    )


def bootstrap_experiments(store: CEECStore, config_dir: Path) -> list[str]:
    experiment_dir = config_dir / "experiments"
    ids = []
    for config_path in sorted(experiment_dir.glob("*.yaml")):
        experiment = experiment_from_config(config_path)
        store.pre_register_experiment(experiment)
        ids.append(experiment.id)
    return ids


def bootstrap(store: CEECStore, config_dir: Path | str) -> dict[str, list[str]]:
    config_dir = Path(config_dir)
    if (store._conn.execute("SELECT COUNT(*) AS n FROM beliefs").fetchone())["n"] > 0:
        raise StoreError("ledger already bootstrapped; refusing to double-bootstrap")
    return {
        "instruments": bootstrap_instruments(store, config_dir),
        "beliefs": bootstrap_beliefs(store, config_dir),
        "goals": bootstrap_goals(store, config_dir),
        "experiments": bootstrap_experiments(store, config_dir),
    }


def _scope(raw: dict[str, Any]) -> models.Scope:
    list_fields = {
        k: tuple(v) for k, v in raw.items() if k in {"substrate", "geometry", "credit"}
    }
    return models.Scope(
        domain=raw.get("domain", "unknown"),
        substrate=list_fields.get("substrate", ()),
        geometry=list_fields.get("geometry", ()),
        credit=list_fields.get("credit", ()),
        budget=raw.get("budget"),
        code_commit=raw.get("code_commit"),
        extra={
            k: v
            for k, v in raw.items()
            if k
            not in {
                "domain",
                "substrate",
                "geometry",
                "credit",
                "budget",
                "code_commit",
            }
        },
    )


def _now() -> str:
    from computronium.ceec.store import now

    return now()
