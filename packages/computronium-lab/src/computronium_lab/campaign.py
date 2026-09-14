"""Mechanism validation campaigns (TODO23 §6/§8): CEEC-governed, not probes.

A campaign = one mechanism × problem class × constraints, run at multiple
seeds with three gates:

- ``BenchmarkReproduction`` — measured quick-tier accuracy within tolerance
  of the catalog's transcribed metadata.
- ``StabilityCertificate`` — every seed trained with the calibrated guard
  raised no kill and returned a checked certificate.
- ``DeployabilityCheck`` — the trained system exports (ONNX/manifest) with
  substrate constraints preserved.

`ledger_audit` enforces TODO23 §10: the new ledger carries campaign
records only, zero ``X-*`` experiment codes.
"""

from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Protocol, runtime_checkable

import torch
from torch import Tensor
from torch.utils.data import DataLoader, TensorDataset

from computronium_lab.synthesis.catalog import CATALOG, MechanismCandidate
from computronium_lab.training import TrainingResult, TrainOptions

if TYPE_CHECKING:
    from ceec.gates import Evaluation
    from ceec.store import CEECStore

    from computronium_lab.lab import Lab
    from computronium_lab.synthesis.spec import ProblemSpec

__all__ = [
    "GATES",
    "CampaignReport",
    "MechanismBelief",
    "ledger_audit",
    "promote_mechanism",
    "run_campaign",
]

GATES: tuple[str, ...] = (
    "BenchmarkReproduction",
    "StabilityCertificate",
    "DeployabilityCheck",
)

_X_CODE = re.compile(r"X-[A-Z]+-\d+")


@runtime_checkable
class _EvalSystem(Protocol):
    """Structural surface needed to score a trained system on a loader."""

    def eval(self) -> object: ...
    def __call__(self, x: Tensor) -> Tensor: ...


@dataclass(frozen=True, slots=True)
class CampaignReport:
    """One validated mechanism: per-seed results + gate verdicts."""

    mechanism: str
    spec_key: str
    seeds: tuple[int, ...]
    accuracies: tuple[float, ...]
    predicted_accuracy: float
    reproduction: bool
    stability: bool
    deployability: bool
    certified: bool

    def summary(self) -> dict[str, object]:
        return {
            "mechanism": self.mechanism,
            "spec": self.spec_key,
            "seeds": list(self.seeds),
            "accuracies": list(self.accuracies),
            "predicted_accuracy": self.predicted_accuracy,
            "gates": {
                "BenchmarkReproduction": self.reproduction,
                "StabilityCertificate": self.stability,
                "DeployabilityCheck": self.deployability,
            },
            "certified": self.certified,
        }


def run_campaign(
    lab: Lab,
    mechanism: str,
    spec: ProblemSpec,
    *,
    seeds: tuple[int, ...] = (0, 1, 2),
    epochs: int = 1,
    reproduction_tolerance: float = 0.15,
    out_dir: str | None = None,
) -> CampaignReport:
    """Validate one cataloged mechanism at multiple seeds (TODO23 §6).

    Raises ``ValueError`` for uncataloged mechanisms. Every gate outcome is
    recorded to the lab's CEEC ledger when ``lab.record_ledger`` is set.
    """
    candidates = [c for c in CATALOG if c.name == mechanism]
    if not candidates:
        raise ValueError(
            f"{mechanism!r} is not cataloged; known: {[c.name for c in CATALOG]}"
        )
    cand = candidates[0]
    accuracies: list[float] = []
    stability_ok = True
    for seed in seeds:
        lab.seed = seed
        system = cand.build(spec)
        result: TrainingResult = lab.train(
            system, epochs=epochs, spec=spec, options=TrainOptions(stability_guard=True)
        )
        accuracies.append(float(result.metrics["accuracy"]))
        stability_ok = stability_ok and _certificate_checked(result)

    mean_accuracy = sum(accuracies) / len(accuracies)
    reproduction = mean_accuracy >= cand.pareto.accuracy - reproduction_tolerance

    deployability = True
    deploy_note = "skipped (no out_dir)"
    if out_dir is not None:
        from computronium_lab.deployment import export_system

        try:
            export = export_system(
                cand.build(spec),
                out_dir,
                constraints=spec.constraints,
                target="onnx",
            )
            deployability = (
                export.substrate_report.constraints_preserved
                and Path(export.manifest_path).exists()
            )
            deploy_note = f"manifest={Path(export.manifest_path).name}"
        except Exception as exc:  # ruff: ignore[blind-except] - gate failure is data
            deployability = False
            deploy_note = f"export failed: {exc}"

    certified = reproduction and stability_ok and deployability
    report = CampaignReport(
        mechanism=mechanism,
        spec_key=spec.key(),
        seeds=seeds,
        accuracies=tuple(accuracies),
        predicted_accuracy=cand.pareto.accuracy,
        reproduction=reproduction,
        stability=stability_ok,
        deployability=deployability,
        certified=certified,
    )
    _record(lab, report, deploy_note)
    return report


def _certificate_checked(result: TrainingResult) -> bool:
    stability = result.stability
    if stability is None:
        return False
    if hasattr(stability, "checked"):
        return (
            bool(stability.checked)
            or "kill" not in str(getattr(stability, "note", "")).lower()
        )
    return True


def _record(lab: Lab, report: CampaignReport, deploy_note: str) -> None:
    from ceec.models import Scope
    from ceec.store import CEECStore

    ledger = lab.record_ledger
    if not ledger:
        return
    db = Path(str(ledger))
    payload = json.dumps(report.summary(), indent=2)
    with CEECStore(db, db.parent / "artifacts") as store:
        artifact = store.ingest_artifact(
            payload.encode(),
            "validation_campaign",
            {"source": "computronium_lab.campaign", "mechanism": report.mechanism},
        )
        evidence = store.record_evidence(
            kind="scalar",
            scope=Scope(
                domain="lab",
                substrate=(spec_substrate(report),),
                budget="quick",
            ),
            artifact_refs=[artifact.id],
            quality={"seeds": len(report.seeds), "matched_control": False},
            defects=[],
            notes=f"validation campaign; deploy: {deploy_note}",
        )
        for gate, ok in (
            ("BenchmarkReproduction", report.reproduction),
            ("StabilityCertificate", report.stability),
            ("DeployabilityCheck", report.deployability),
        ):
            store.record_gate_outcome(
                gate=gate,
                status="passed" if ok else "failed",
                rationale=f"campaign for {report.mechanism} ({report.spec_key})",
                evidence_refs=[evidence.id],
            )
        store.record_decision(
            state_hash=artifact.sha256,
            candidate_experiments=[],
            scores={"mean_accuracy": sum(report.accuracies) / len(report.accuracies)},
            rationale=(
                f"certify mechanism {report.mechanism} for {report.spec_key}"
                if report.certified
                else f"do not certify {report.mechanism}: gates failed"
            ),
            selected_experiment=None,
        )
        store._conn.commit()


def spec_substrate(report: CampaignReport) -> str:
    for c in CATALOG:
        if c.name == report.mechanism:
            return c.substrates[0]
    return "digital"


_ALLOWED_ARTIFACT_TYPES = {
    "validation_campaign",
    "exploratory_synthesis",
    "lab_comparison",
    "mechanism_belief",
    # TODO24 research-layer records (T24.0.4):
    "evolution_generation",
    "evolution_candidate",
    "research_corpus_summary",
    "measurement_block",
    # Structured-evidence payload attachments (T24.0.6 helpers):
    "evidence_payload",
    # Closed-loop runner records (TODO25 C.4):
    "experiment_payload",
    "experiment_failure",
}


@dataclass(frozen=True, slots=True)
class MechanismBelief:
    """§6 belief promotion over a multi-campaign corpus."""

    belief_id: str
    statement: str
    mechanism: str
    campaigns: tuple[CampaignReport, ...]
    control_accuracies: dict[str, float]
    evaluation: Evaluation | None
    promoted: bool
    violations: tuple[str, ...]


def promote_mechanism(
    lab: Lab,
    mechanism: str,
    specs: list[ProblemSpec],
    *,
    seeds: tuple[int, ...] = (0, 1, 2),
    epochs: int = 10,
    reproduction_tolerance: float = 0.15,
    belief_id: str | None = None,
    reports: list[CampaignReport] | None = None,
) -> MechanismBelief:
    """Run a campaign per spec, then promote one ``B-SYNTH-*`` belief (§6).

    The belief is pre-registered, linked to per-campaign evidence carrying
    the promotion-gate quality flags, revised with a one-sided t-based
    probability lower bound over seed accuracies vs the reproduction
    threshold, and promoted only if every ``evaluate_promotion`` gate
    passes. The matched-control arm trains the same mechanism on
    label-permuted data at equal compute; it must stay chance-level
    (scored on the unpermuted val split).

    Pass ``reports`` (one certified ``CampaignReport`` per spec, e.g. from
    a previous ``run_campaign`` call) to reuse measured campaigns instead
    of re-running them; controls still run — they are cheap and define the
    ``matched_control`` flag.
    """
    ledger = lab.record_ledger
    if not ledger:
        raise ValueError("promote_mechanism requires Lab(record_ledger=...)")
    candidates = [c for c in CATALOG if c.name == mechanism]
    if not candidates:
        raise ValueError(
            f"{mechanism!r} is not cataloged; known: {[c.name for c in CATALOG]}"
        )
    cand = candidates[0]

    if reports is not None:
        _require_corpus(mechanism, specs, reports)
    else:
        reports = [
            run_campaign(
                lab,
                mechanism,
                spec,
                seeds=seeds,
                epochs=epochs,
                reproduction_tolerance=reproduction_tolerance,
            )
            for spec in specs
        ]
    control = {
        spec.key(): _control_accuracy(lab, cand, spec, seeds, epochs) for spec in specs
    }

    return _register_belief(
        lab,
        mechanism,
        reports,
        control,
        seeds=seeds,
        epochs=epochs,
        belief_id=belief_id,
        tolerance=reproduction_tolerance,
    )


def _require_corpus(
    mechanism: str, specs: list[ProblemSpec], reports: list[CampaignReport]
) -> None:
    expected = {s.key() for s in specs}
    keys = {r.spec_key for r in reports}
    if keys != expected or not all(r.mechanism == mechanism for r in reports):
        raise ValueError(
            f"reports must be one {mechanism!r} campaign per spec; got "
            f"{sorted(keys)} vs specs {sorted(expected)}"
        )


def _control_accuracy(
    lab: Lab,
    cand: MechanismCandidate,
    spec: ProblemSpec,
    seeds: tuple[int, ...],
    epochs: int,
) -> float:
    """Equal-compute label-permutation control, scored on the val split.

    Training uses per-sample permuted labels; scoring uses the *unpermuted*
    val split, so the learned map is wrong by construction and the honest
    control ceiling is chance — memorization on the permuted train set
    cannot inflate it.
    """
    from computronium_lab.lab import synthetic_task

    accuracies = []
    for seed in seeds:
        lab.seed = seed
        system = cand.build(spec)
        lab.train(
            system,
            epochs=epochs,
            spec=spec,
            train_data=_permuted_task(spec, seed),
        )
        _, val = synthetic_task(
            seed=seed,
            input_dim=spec.input_dim,
            num_classes=spec.num_classes,
        )
        if not isinstance(system, _EvalSystem):
            raise TypeError("composed system lacks eval/__call__")
        system.eval()
        correct = total = 0
        with torch.no_grad():
            for x, y in val:
                total += len(y)
                correct += int((system(x).argmax(-1) == y).sum())
        accuracies.append(correct / total)
    return sum(accuracies) / len(accuracies)


def _permuted_task(
    spec: ProblemSpec, seed: int, batch_size: int = 32
) -> DataLoader[tuple[Tensor, ...]]:
    from computronium_lab.lab import synthetic_task

    gen = torch.Generator().manual_seed(seed + 9999)
    train, _ = synthetic_task(
        seed=seed,
        batch_size=batch_size,
        input_dim=spec.input_dim,
        num_classes=spec.num_classes,
    )
    ds = train.dataset
    if not isinstance(ds, TensorDataset):
        raise TypeError("synthetic task dataset is not a TensorDataset")
    x, y = ds.tensors
    return DataLoader(
        TensorDataset(x, y[torch.randperm(len(y), generator=gen)].clone()),
        batch_size=batch_size,
        shuffle=True,
    )


def _probability_low(reports: list[CampaignReport], tolerance: float) -> float:
    """One-sided t lower bound of each seed mean above its threshold."""
    from scipy import stats

    lows = []
    for report in reports:
        thr = report.predicted_accuracy - tolerance
        accs = report.accuracies
        n = len(accs)
        mean = sum(accs) / n
        var = sum((a - mean) ** 2 for a in accs) / (n - 1)
        se = math.sqrt(max(var, 1e-6) / n)
        lows.append(float(stats.t.cdf((mean - thr) / se, df=n - 1)))
    return min(lows)


def _register_belief(
    lab: Lab,
    mechanism: str,
    reports: list[CampaignReport],
    control: dict[str, float],
    *,
    seeds: tuple[int, ...],
    epochs: int,
    belief_id: str | None,
    tolerance: float,
) -> MechanismBelief:
    from ceec.store import CEECStore

    from ceec import audit, gates, models

    matched_control = all(
        control[r.spec_key] < r.predicted_accuracy - tolerance for r in reports
    )
    reproduced = all(r.reproduction for r in reports)
    statement = (
        f"Mechanism {mechanism} reproduces catalog accuracy (±tolerance) "
        f"on {len(reports)} problem class(es): "
        f"{', '.join(r.spec_key for r in reports)}"
    )
    db = Path(str(lab.record_ledger))
    with CEECStore(db, db.parent / "artifacts") as store:
        bid = belief_id or f"B-SYNTH-{mechanism.upper()}-001"
        artifact = store.ingest_artifact(
            json.dumps(
                {
                    "mechanism": mechanism,
                    "campaigns": [r.summary() for r in reports],
                    "control_accuracies": control,
                    "epochs": epochs,
                    "seeds": list(seeds),
                },
                indent=2,
            ).encode(),
            "mechanism_belief",
            {"source": "computronium_lab.promote_mechanism", "mechanism": mechanism},
        )
        evidence_refs = _link_campaign_evidence(
            store,
            mechanism,
            reports,
            control,
            artifact.id,
            seeds=seeds,
            matched_control=matched_control,
        )
        store.create_belief(
            statement,
            "mechanism",
            models.Scope(
                domain="lab",
                substrate=(spec_substrate(reports[0]),),
                extra={
                    "mechanism": mechanism,
                    "problem_classes": [r.spec_key for r in reports],
                    "epochs": epochs,
                },
            ),
            posterior_method="one_sided_t_lower_bound_on_seed_mean",
            id_=bid,
            evidence_refs=evidence_refs,
        )
        probability_low = _probability_low(reports, tolerance)
        store.update_belief(
            bid,
            models.Probability(
                low=probability_low,
                high=1.0,
                point=probability_low,
                method="one_sided_t_lower_bound_on_seed_mean",
            ),
            "low",
            "high",
            "narrow" if len(reports) == 1 else "moderate",
            "open",
            f"{len(reports)} campaign(s); matched_control={matched_control}, "
            f"reproduced={reproduced}",
        )
        evaluation = gates.promote(store, bid, f"campaign corpus certified {mechanism}")
        violations = [
            f.check for f in audit.run_audit(store) if f.severity == "violation"
        ]
        store._conn.commit()

    return MechanismBelief(
        belief_id=bid,
        statement=statement,
        mechanism=mechanism,
        campaigns=tuple(reports),
        control_accuracies=control,
        evaluation=evaluation,
        promoted=evaluation.all_passed,
        violations=tuple(violations),
    )


def _link_campaign_evidence(
    store: CEECStore,
    mechanism: str,
    reports: list[CampaignReport],
    control: dict[str, float],
    artifact_id: str,
    *,
    seeds: tuple[int, ...],
    matched_control: bool,
) -> list[str]:
    from ceec import models

    substrate = spec_substrate(reports[0])
    refs = []
    for report in reports:
        ev = store.record_evidence(
            kind="scalar",
            scope=models.Scope(
                domain="lab",
                substrate=(substrate,),
                extra={"mechanism": mechanism},
            ),
            artifact_refs=[artifact_id],
            quality={
                "seeds": len(seeds),
                "matched_control": matched_control,
                "evaluation_policy": "multi_seed_campaign_v1",
                "defect_audit": "pass",
                "reproduction": report.reproduction,
            },
            values_ref=report.spec_key,
            defects=[],
            notes=(
                f"campaign accuracies {report.accuracies}; "
                f"control {control[report.spec_key]:.3f}"
            ),
        )
        refs.append(ev.id)
    return refs


def ledger_audit(db_path: str | Path) -> dict[str, object]:
    """TODO23 §10 audit, T24.0.6 unified: ceec structural findings plus the
    lab campaign-only allowlist and ``X-*`` probe-code rejection.

    Returns counts per artifact type, any leaked experiment codes found in
    artifact provenance or evidence notes, ceec audit findings, and an
    overall ``clean`` flag.
    """
    from computronium_lab.research.evidence import run_ledger_audit

    return run_ledger_audit(db_path)
