"""TODO23 §6/§10 — CEEC-governed validation campaign + ledger audit."""

from __future__ import annotations

from typing import TYPE_CHECKING

from computronium_lab import Constraints, Lab

if TYPE_CHECKING:
    from pathlib import Path
from computronium_lab.campaign import (
    GATES,
    ledger_audit,
    promote_mechanism,
    run_campaign,
)


def test_campaign_certifies_backprop_mlp(tmp_path: Path) -> None:
    lab = Lab(seed=0, record_ledger=str(tmp_path / "ledger.db"))
    spec = lab.specify("classification", "synthetic", constraints=Constraints())
    report = run_campaign(
        lab,
        "backprop_mlp",
        spec,
        seeds=(0, 1),
        epochs=20,
        out_dir=str(tmp_path / "exports"),
    )
    assert report.reproduction, (
        f"mean {sum(report.accuracies) / len(report.accuracies):.3f} vs predicted {report.predicted_accuracy:.3f}"
    )
    assert report.stability
    assert report.deployability
    assert report.certified
    assert set(report.summary()["gates"]) == set(GATES)  # type: ignore[arg-type]


def test_campaign_certifies_ntm_classifier(tmp_path: Path) -> None:
    """Ontology-NTM row: its own measured campaign (TODO23 §12, 2026-09-13)."""
    lab = Lab(seed=0, record_ledger=str(tmp_path / "ledger.db"))
    spec = lab.specify("classification", "synthetic", constraints=Constraints())
    report = run_campaign(
        lab,
        "ntm_classifier",
        spec,
        seeds=(0, 1, 2),
        epochs=10,
        out_dir=str(tmp_path / "exports"),
    )
    assert report.certified, report.summary()


def test_campaign_rejects_uncataloged_mechanism() -> None:
    lab = Lab(seed=0)
    spec = lab.specify("classification", "synthetic")
    try:
        run_campaign(lab, "nonexistent_mlp", spec)
    except ValueError as exc:
        assert "not cataloged" in str(exc)
    else:
        raise AssertionError("uncataloged mechanism must raise")


def test_promote_mechanism_from_campaign_corpus(tmp_path: Path) -> None:
    """§6: a multi-campaign corpus promotes a B-SYNTH-* mechanism belief."""
    from ceec.store import CEECStore

    ledger = tmp_path / "ledger.db"
    lab = Lab(seed=0, record_ledger=str(ledger))
    specs = [
        lab.specify("classification", "synthetic", constraints=Constraints()),
        lab.specify(
            "classification",
            "synthetic",
            constraints=Constraints(),
            input_dim=32,
            num_classes=2,
        ),
    ]
    belief = promote_mechanism(lab, "backprop_mlp", specs, epochs=20)

    assert all(r.certified for r in belief.campaigns)
    assert belief.promoted, [
        r.rationale for r in (belief.evaluation.results if belief.evaluation else [])
    ]
    assert not belief.violations
    assert belief.evaluation is not None
    with CEECStore(ledger, tmp_path / "artifacts") as store:
        assert store.current_status(belief.belief_id) == "promoted"
        assert store.get_belief(belief.belief_id).type == "mechanism"
    audit = ledger_audit(ledger)
    assert audit["clean"], audit


def test_promote_mechanism_refuses_unreproduced_corpus(tmp_path: Path) -> None:
    """A corpus that fails BenchmarkReproduction must not promote (§6)."""
    from ceec.store import CEECStore

    ledger = tmp_path / "ledger.db"
    lab = Lab(seed=0, record_ledger=str(ledger))
    spec = lab.specify("classification", "synthetic", constraints=Constraints())
    belief = promote_mechanism(lab, "backprop_mlp", [spec], epochs=1)

    assert not belief.campaigns[0].reproduction
    assert not belief.promoted
    with CEECStore(ledger, tmp_path / "artifacts") as store:
        assert store.current_status(belief.belief_id) != "promoted"


def test_promote_mechanism_accepts_precomputed_reports(tmp_path: Path) -> None:
    """Budget reuse: prior campaigns feed promotion without re-running."""
    ledger = tmp_path / "ledger.db"
    lab = Lab(seed=0, record_ledger=str(ledger))
    spec = lab.specify("classification", "synthetic", constraints=Constraints())
    prior = run_campaign(lab, "backprop_mlp", spec, seeds=(0, 1, 2), epochs=20)
    belief = promote_mechanism(lab, "backprop_mlp", [spec], epochs=20, reports=[prior])
    assert belief.promoted, belief.violations
    assert belief.campaigns[0].accuracies == prior.accuracies


def test_promote_mechanism_rejects_mismatched_corpus(tmp_path: Path) -> None:
    ledger = tmp_path / "ledger.db"
    lab = Lab(seed=0, record_ledger=str(ledger))
    spec = lab.specify("classification", "synthetic", constraints=Constraints())
    other = run_campaign(lab, "ntm_classifier", spec, seeds=(0,), epochs=1)
    try:
        promote_mechanism(lab, "backprop_mlp", [spec], reports=[other])
    except ValueError as exc:
        assert "one 'backprop_mlp' campaign per spec" in str(exc)
    else:
        raise AssertionError("mismatched corpus must raise")


def test_ledger_audit_clean(tmp_path: Path) -> None:
    ledger = tmp_path / "ledger.db"
    lab = Lab(seed=0, record_ledger=str(ledger))
    spec = lab.specify("classification", "synthetic", constraints=Constraints())
    run_campaign(lab, "backprop_mlp", spec, seeds=(0,), epochs=1)

    audit = ledger_audit(ledger)
    assert audit["campaign_only"], audit
    assert audit["x_codes"] == [], audit
    assert audit["clean"]
    assert "validation_campaign" in audit["artifact_types"]  # type: ignore[operator]


def test_ledger_audit_flags_x_code(tmp_path: Path) -> None:
    # A ledger seeded with a legacy probe-code note must fail the audit.
    import sqlite3

    from ceec.store import CEECStore
    from computronium_lab.campaign import ledger_audit

    ledger = tmp_path / "dirty.db"
    store = CEECStore(ledger, tmp_path / "artifacts")
    store.close()

    conn = sqlite3.connect(ledger)
    conn.execute(
        "INSERT INTO evidence (id, kind, scope, created_at, notes) VALUES "
        "(?, 'scalar', '{}', '2026-01-01T00:00:00', 'legacy probe X-ALI-001')",
        ("EV_test_dirty",),
    )
    conn.commit()
    conn.close()

    audit = ledger_audit(ledger)
    assert "X-ALI-001" in audit["x_codes"]  # type: ignore[operator]
    assert not audit["clean"]
