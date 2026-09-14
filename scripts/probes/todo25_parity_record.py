"""F5 step 2 (TODO25): record the parity boundary belief from the probe
result and run the CEEC-Core §19 boundary gates via ``declare_boundary``.

Reads ``scratch/todo25_parity_boundary.json`` (probe output, cert tier:
120ep x 3 seeds + lr lever sweep) and writes the ledger
``scratch/todo25_parity.sqlite3``.

Usage: uv run python scripts/probes/todo25_parity_record.py
"""

from __future__ import annotations

import json
from pathlib import Path

from ceec.gates import declare_boundary
from ceec.store import CEECStore

from ceec import models

RESULT = Path("scratch/todo25_parity_boundary.json")
LEDGER = Path("scratch/todo25_parity.sqlite3")


def main() -> int:
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    if not result["boundary_supported"]:
        print("boundary not supported; nothing to record")
        return 1
    certified = result["certified"]

    store = CEECStore(LEDGER, LEDGER.parent / "todo25_parity_artifacts")
    scope = models.Scope(
        domain="research",
        substrate=("digital",),
        budget="certified",
        extra={"problem_class": "sequence_parity", "probe": "todo25_f5"},
    )
    artifact = store.ingest_artifact(
        json.dumps(result, sort_keys=True).encode(),
        "research_corpus_summary",
        {"problem_class": "sequence_parity", "mechanism": "ntm_classifier"},
    )
    evidence = store.record_evidence(
        kind="vector",
        scope=scope,
        artifact_refs=[artifact.id],
        quality={
            "seeds": len(certified["seeds"]),
            "matched_control": True,
            "evaluation_policy": "certified_operating_point_120ep",
            "defect_audit": "pass",
            "integrity_checks": "pass",
            "known_levers_exhausted": True,
        },
        axes=["seed"],
        values_ref="scratch/todo25_parity_boundary.json#certified.accuracies",
        notes=(
            f"parity certified at chance: accuracies "
            f"{[round(a, 4) for a in certified['accuracies']]} "
            f"(mean {certified['mean']:.4f}, verdict {certified['verdict_rule']}); "
            f"lr sweep 0.01/0.1/0.3 all at chance; defect hunt: task "
            f"pipeline shared with last_symbol (0.918+ @ 120ep)"
        ),
    )
    belief = store.create_belief(
        "NTM-classifier sequence-parity accuracy is at chance (0.5) at the "
        "certified operating point (120 epochs x 3 seeds); no tested lr "
        "lever breaks chance",
        "mechanism",
        scope,
        posterior_method="certified_chance_boundary",
        id_="B-PARITY-CHANCE-001",
        evidence_refs=[evidence.id],
    )
    store.update_belief(
        belief.id,
        models.Probability(low=0.0, high=0.05, method="certified_chance_boundary"),
        "low",
        "high",
        "narrow",
        "open",
        "certified chance result; rescue probability high capped at the "
        "boundary threshold pending a new mechanism class",
    )
    evaluation = declare_boundary(
        store, belief.id, "TODO25 F5: certified chance boundary (parity)"
    )
    print(
        json.dumps(
            {
                "belief": belief.id,
                "status": store.current_status(belief.id),
                "gates": [
                    {"gate": g.gate, "passed": g.passed, "detail": g.rationale}
                    for g in evaluation.results
                ],
                "all_passed": evaluation.all_passed,
            },
            indent=2,
        )
    )
    store._conn.commit()
    store.close()
    return 0 if evaluation.all_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
