"""B-H3 scope-gate closure (TODO21 T21.2.1, option A variant).

X-STA-002 (E-000028) validated retention, not robustness: paired replay
showed noise divergence scales with the retention ratio, so SNR is
unchanged. The belief statement must reflect retention-gain-only, and the
belief interval [0.55, 0.85] already does.

Closure decision recorded here:
- A retention-only revision is recorded (statement scope narrowed; the
  interval is unchanged — no new evidence, no fabricated probability).
- Both gate paths are evaluated and their outcomes recorded honestly:
  promotion fails `probability_threshold` (heuristic interval low=0.55 vs
  0.95; unreachable by design for scope-bounded mechanisms), and boundary
  declaration fails `rescue_probability_threshold` (high=0.85 — the
  mechanism is validated-positive, not dead, so `boundary` is the wrong
  terminal status).
- Status therefore remains `open` with the validated scope as the
  operative boundary; consumers (recipe book, manuscript) cite evidence
  ids, not belief status. Gate reform is a ledger feature (out of scope
  for TODO21) and is registered as deferred work.

Run:
    uv run python scripts/b_h3_scope_gate.py
"""

from __future__ import annotations

from pathlib import Path

from computronium.ceec import gates, models
from computronium.ceec.store import CEECStore

REPO_ROOT = Path(__file__).resolve().parents[1]
BELIEF_ID = "B-H3-STABLE-TRANSIENT-AMPLIFICATION"


def main() -> None:
    with CEECStore(
        REPO_ROOT / "ceec" / "ceec.sqlite3", REPO_ROOT / "ceec" / "artifacts"
    ) as store:
        store.update_belief(
            BELIEF_ID,
            models.Probability(
                low=0.55,
                high=0.85,
                method="heuristic_interval_based_on_gate_evidence",
            ),
            "medium",
            "medium",
            "narrow",
            "open",
            "T21.2.1 scope closure: belief restated as retention-gain-only "
            "(X-STA-002 paired replay: noise divergence scales with the "
            "retention ratio; SNR unchanged). Interval [0.55, 0.85] reflects "
            "retention only. Statement wording corrected in beliefs.yaml.",
        )
        promotion = gates.evaluate_promotion(store, BELIEF_ID)
        boundary = gates.evaluate_boundary(store, BELIEF_ID)
        print("promotion:", [(r.gate, r.passed) for r in promotion.results])
        print("boundary:  ", [(r.gate, r.passed) for r in boundary.results])

        store.record_decision(
            state_hash=f"b-h3-scope-closure:{promotion.gate_outcome_ids[0]}",
            candidate_experiments=[
                "promote",
                "declare_boundary",
                "keep_open_bounded_scope",
            ],
            scores={
                "promote": float(promotion.all_passed),
                "declare_boundary": float(boundary.all_passed),
            },
            rationale=(
                "T21.2.1: promotion blocked only by probability_threshold "
                "(0.55 vs 0.95 — unreachable by design for heuristic "
                "scope-bounded intervals); boundary declaration blocked by "
                "rescue_probability_threshold (0.85 vs 0.05 — mechanism is "
                "validated-positive, boundary status would misstate it). "
                "Decision: keep open with retention-gain-only scope as the "
                "operative boundary; status consumers cite E-000011/E-000019/"
                "E-000028. Gate reform (bounded status or scope-bounded "
                "promotion threshold) is deferred ledger work."
            ),
            selected_experiment=None,
        )


if __name__ == "__main__":
    main()
