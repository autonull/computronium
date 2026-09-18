# CEEC — Controlled Epistemic Evidence Chain

CEEC is the epistemic operating system of this repository: an append-only
evidence ledger plus gate/decision machinery that turns raw experimental
results into **certified** claims — promotion, boundary, or quarantine — and
makes overclaiming structurally impossible rather than a matter of
discipline.

**Core rule:** evolution/campaigns produce evidence; gates dispose; claims
only at certified tier. An idea is `promoted`, boundary'd (a certified dead
end), `quarantined`, or honestly `open` — never limbo.

| | |
|---|---|
| Canonical implementation | `packages/ceec-core` (uv workspace member; import `ceec`; console script `ceec`) |
| Legacy import path | `computronium/ceec/` — a pure re-export shim of the package |
| Origin | TODO19 Epistemic Foundry; CEEC-Core v1.0 |
| Normative policies | `docs/ceec/` (linked per-section below) |
| Practitioner walkthrough | `docs/research/todo24/ceec_guide.md` |

The package is standalone by design: zero `computronium` imports, stdlib +
pydantic only, so the governance layer cannot import the thing it governs.

---

## Why it exists

The project's dominant failure mode is self-deception about learning
mechanisms: saturating metrics, broken instruments, p-hacked operating
points, "it underperformed" conclusions drawn from a mis-wired harness.
CEEC has caught three real instances of exactly this:

1. **Chance-band miscalibration** — the first parity-boundary screen used a
   fixed ±0.03 band; the honest band at n_eval=32 is ±0.177. The evidence
   discipline (eval size recorded, verdict derived from it) surfaced the
   error *before* a false boundary was certified. Now codified as
   `ceec.builders.chance_verdict`.
2. **Saturation censoring** — 6 of 10 catalog rows saturate flat
   classification at 20ep, making rank-based hypothesis tests degenerate.
   The H24.2 belief was left `open` rather than scored on censored data;
   the censoring finding drove the non-saturating `flat_classification_hard`
   corpus class, which produced the uncensored verdict.
3. **Instrument mismatch** — the "ψ underperforms" round-1 result traced to
   a readout that cannot run the registered continual benchmark at all.
   Instrument discipline forced an instrument-boundary `measurement_block`
   instead of a false mechanism claim.

A cheaper process would have certified all three the wrong way.

## The chain

```
Experiment → Artifact → Evidence → Derived → Belief → Status
           → Goal Priority → Next Experiment → Decision
```

Every scientific move is a typed, id-prefixed record in one ledger.

## Object model (`ceec.models`)

| Kind | Id prefix | Mutability |
|---|---|---|
| `Scope` | — | frozen value object (domain, substrate, budget) |
| `Artifact` | `sha256:<hex>` | content-addressed, immutable |
| `Evidence` | `E-` | append-only; structured kinds require `axes` + `values_ref` |
| `Derived` | `D-` | append-only (`mechanism_schema`, `correction`, `decision_quality`) |
| `Belief` | `B-` / `I-` | identity immutable; probability changes append revisions |
| `Goal` | — | identity immutable; priority changes append revisions |
| `Experiment` | `X-` | status flows `draft → pre_registered → running → completed \| failed` |
| `Decision` | `DEC-` | append-only (selection, scores, overrides, constraints) |
| `GateOutcome` / `StatusChange` / `CalibrationRecord` / `InstrumentNote` | — | append-only |

Belief types: `instrument` (`I-`), `mechanism`, `generality`, `defect`.
Boundary is a *status*, not a type.

## Ledger

- SQLite; default location `ceec/ceec.sqlite3` with content-addressed
  artifacts under `ceec/artifacts/`.
- Append-only enforced by database triggers — the public API exposes no
  update/delete for evidence, decisions, gate outcomes, status changes, or
  calibration records. Belief/goal revisions are append-only too; history
  is recoverable.
- Corrections ingest a new artifact and record a `correction` Derived with
  `supersedes` relations; a correction that invalidates a measurement
  quarantines or reopens the affected belief with the correction as
  trigger evidence.
- Campaign ledgers are scoped SQLite files (`scratch/todo24_h24.sqlite3`,
  `scratch/todo25_parity.sqlite3`, git-ignored); the main ledger holds
  bootstrap round history and instrument beliefs.

Details: `docs/ceec/LEDGER_POLICY.md`.

## Statuses and gates

| Status | Meaning | Gate condition |
|---|---|---|
| `open` | live question | — |
| `promoted` | certified claim | `probability_low >= 0.95` + all §19 quality gates |
| `boundary` | certified dead end | `rescue_probability_high <= 0.05` + `defect_hunt_passed` |
| `quarantined` | untrusted (instrument defect, suspect provenance) | propagates to material dependents |

- Current status = latest `status_changes.to_status`; *effective* status
  additionally propagates quarantine and stale-dependency signals
  (`ceec.gates.effective_status`).
- Reopen requires a declared credible trigger (estimated rescue
  probability `> 0.10`).
- §19 quality gates include `defect_audit`, `integrity_checks`,
  `known_levers_exhausted`, matched controls, seeds — exact spellings
  validated by `ceec.builders.gate_evidence` against the gate readers.
- Quarantine of an instrument blocks promotion/boundary of dependent
  beliefs and selection of materially dependent experiments;
  unquarantine cascades back. Registry:
  `configs/ceec/instruments.yaml`, `docs/ceec/INSTRUMENT_BELIEFS.md`.

Thresholds and probability policy: `docs/ceec/COMPUTRONIUM_PROFILE.md`.

## Experiment selection (§22)

`ceec.selection.decide(store, profile, rationale, candidate_ids=...)`:

1. Hard-constraint filter runs **before** scoring — `coordinate_valid`,
   `pre_registration_complete`, `no_quarantined_dependencies`,
   `budget_within_limit`, `controls_present_or_justified`, `seed_plan_present`,
   `evaluation_policy_present`, `structured_evidence_plan_present`,
   `instrument_valid_for_claim`, `frozen_theta_audit_for_psi_only_claims`,
   `identity_card_for_new_primitive`. No override may bypass them.
2. Eligible candidates score `ExpectedValue / Cost^gamma` (γ = 1.0; cost =
   walltime + 0.25·memory + 0.5·human_review + 0.05·storage, normalized).
3. `candidate_ids` scopes the pool (e.g. one evolution generation) so
   unrelated pre-registered experiments cannot hijack selection.
4. Overrides select a non-top-ranked *eligible* candidate, require a
   rationale, and are append-only in the decision record. A
   `select_experiment` override on a single-eligible-candidate pool is
   vacuous — validated but not recorded, so §24 `override_rate` keeps
   signal for real selections-with-alternatives.

Pre-registration requirements (fields, controls policy, falsification and
overturn criteria, status flow): `docs/ceec/EXPERIMENT_PRE_REGISTRATION.md`.

## Calibration (§24)

Every pre-registered prediction with an explicit probability is scored
against its outcome: `Brier = (p−y)²`, log score where a declared point
reduction exists. `ceec.calibration` provides:

- `calibration_report(store)` — predicted vs observed, mean Brier,
  promotion/boundary durability, reopen/quarantine/override rates.
- `review_flags(report)` — review triggers: promotion-reversal or
  boundary-reopen rate > 0.20, `override_rate > 0.20`, quarantine spike
  (≥ 3 in a round).
- `belief_drift(store, tau=0.15)` + `review_belief(...)` — the §24 drift
  cadence: a belief whose Brier drifts > τ across rounds flags for review;
  the review is recorded (`acknowledge` → instrument note; `reopen` /
  `quarantine` → gated status change).

Policy: `docs/ceec/CALIBRATION_POLICY.md`.

## The closed loop

`ceec.run.run_experiment(store, experiment, probe, evaluate=...)` makes
"every certified measurement is pre-registered with a recorded Decision"
structural, not procedural:

```
pre-register (builder draft or pre_registered id)
  → §22 single-candidate decision   # outcome generated strictly after this
  → probe callable
  → artifact + evidence ingestion   # probe exceptions record `failed`, never raise
  → calibration outcome
  → optional boundary/promotion evaluation
```

Supporting instruments:

- `ceec.builders` — `experiment(...)` (auto `created_at`, design defaults,
  tier→budget map), `gate_evidence(...)`/`quality_flags(...)` (§18/§19
  spellings, validated against gate readers), `chance_verdict(accuracies,
  n_eval)` (2·binomial-SE band + across-seed mean rule; canonical home is
  `ceec.stats`).
- `ceec.audit.audit_decisions(store, record=False)` — decision-quality
  findings (unresolved selected experiment, missing override rationale,
  candidate-vs-later-measurement-block overlap); `run_audit(store)` for
  full-ledger integrity, including the §27 anti-pattern extensions
  (single-seed promotion attempt, untested-lever boundary declaration,
  silent scalarization) and campaign-ledger instrument gating.
- `ceec.report.render_ledger(store, record_rollups=False)` — markdown/JSON
  rollup; `Lab.research_report(...)` writes it beside the corpus report.
- `ceec.bootstrap` seeds instruments, hypotheses, goals, and
  pre-registered experiments from `configs/ceec/`.

## Profiles and the Session façade (TODO26)

The kernel is parameterized by a `ceec.profile.Profile`: gate thresholds
(`Thresholds`), budget vocabulary (`budget_tiers`, `tier_budget`,
`default_cost`), the hard-constraint registry (`Constraint` tuples —
`CORE_CONSTRAINTS` plus the `coordinate_constraint(validator)` factory),
and the evidence quality schema (`QualitySchema`, validated at
`record_evidence`; undeclared keys stay open per spec §6). Domain
adapters may only add constraints and declare vocabulary — never weaken
gate families (§17). `LedgerRole` (`main | campaign | scratch`) is
stamped into `ledger_meta` at init; `policy_version` (TODO25 #10b) is
stamped from the profile onto every Decision and CalibrationRecord row.
`Scope` is an open dimension map built with `Scope.of(**dims)`.

Applications use the `Session` façade instead of hand-assembling
payloads:

```python
from ceec.profile import LedgerRole
from ceec.session import ledger

with ledger(LEDGER_PATH, PROFILE, role=LedgerRole.CAMPAIGN) as sess:
    draft = sess.experiment(question=..., prediction=..., scope=...,
                            tier="certified", targets=["B-1"])
    run = sess.run(draft, probe, evaluate="boundary")   # or sess.record_result
    report = sess.close_round()                         # render+audit+drift flags
```

`Session.decide(focus_id=...)` pre-checks the focus candidate's hard
constraints natively (no StoreError fallback), `Session.render` writes
the rollup, and `Session.close_round(fail_on_trigger=True)` is the CLI
equivalent of TODO25 #10c. `ceec.derived` registers recomputable
`summary`/`relation` operators (`mean`, `median`, `spread`, `contrast`,
`slope`, `dominance`, `replication`, `chance_band`) over ledger inputs;
`compute_derived` records rows that recompute byte-identically from the
ledger alone.

## CLI

```
ceec init|bootstrap|migrate|propose|decide|audit|calibration-report|
    status-history|quarantine-report|emit-schema|export
```

Equivalent: `uv run python -m ceec.cli <command>` (legacy shim:
`uv run python -m computronium.ceec.cli`). `--ledger-dir` selects the
store; export writes derived JSON/markdown summaries, never primary
records.

## Mechanism schemas

Generality beliefs extracted from gated evidence (supporting scopes,
evidence refs, failure boundaries, verification levels). Schemas require
at least one promoted claim or one defect-hunted boundary in the target
scope — nothing is emitted from open beliefs. History and emitted schemas:
`docs/ceec/MECHANISM_SCHEMAS.md`.

---

## Honest assessment

**Is it helping?** Yes — measured, not aspirational. The three catches
above are the metric that matters: every one would have produced a wrong
certified claim under a lighter process. The ceremony cost, the usual
objection to governance layers, dropped sharply once Phase C landed the
builders and the closed loop: a fresh ledger built end-to-end through
`run_experiment` now audits clean with zero hand-assembled payloads.

**Where the process still leaks:**

1. **Multi-ledger ambiguity.** Three ledgers exist (main bootstrap ledger,
   two campaign ledgers) with no machine-readable statement of which owns
   what. Beliefs in a campaign ledger cannot be gated against main-ledger
   instruments. An ownership/role field per ledger (recorded at `init`)
   would make `run_audit` enforce it.
2. **Policy semantics are unversioned in the data.** The vacuous-override
   rule changed what `override_rate` means; pre-change ledgers keep the
   inflated rate and nothing in the data distinguishes them. Decisions and
   calibration records should stamp a `policy_version`.
3. **Round-close is manual.** Rendering, auditing, and reviewing drift
   flags are separate commands; a single `ceec close-round` (render +
   audit + review-flags, failing non-zero on triggers) would make the
   cadence mechanical.
4. **Documentation drift.** The shim (`computronium/ceec`) and the package
   (`ceec`) both appear in older docs; this file is now the canonical
   entry point — deep-dive policies live in `docs/ceec/`, round history in
   `docs/ceec/EPISTEMIC_FOUNDRY_REPORT.md` (frozen narrative) and in the
   ledgers themselves.
